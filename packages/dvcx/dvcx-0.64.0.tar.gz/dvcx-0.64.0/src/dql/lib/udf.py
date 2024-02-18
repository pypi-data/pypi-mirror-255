import inspect
import types
from abc import ABC
from typing import Callable

from dql.query import udf
from dql.query.schema import DatasetRow
from dql.sql.types import Int, String


class UDFBase(ABC):
    DEF_OUTPUT_NAME = "result"
    DEF_OUTPUT_TYPE = String

    def __init__(self, params=None, output=None, batch=1):
        sign_params, sign_output = self._get_signature(self.process)

        self._params = params or sign_params
        self._output = output or sign_output
        self._batch = batch

    @property
    def params(self):
        return self._params

    @property
    def output(self):
        return self._output

    @property
    def batch(self):
        return self._batch

    @property
    def name(self):
        return self.__class__.__name__

    def to_udf_wrapper(self):
        udf_wrapper = udf(params=self.params, output=self.output, batch=self.batch)
        return udf_wrapper(self)

    def setup(self):  # noqa: B027
        """Initialization process executed on each worker before processing begins.
        This is needed for tasks like pre-loading ML models prior to scoring.
        """

    def process(self, *args, **kwargs):
        """Abstract processing method that needs to be re-defined in child classes."""
        NotImplementedError(f"UDF processing is not implemented in class {self.name}")

    def validate_results(self, results, *args, **kwargs):
        return results

    def __call__(self, *args, **kwargs):
        results = self.process(*args, **kwargs)
        return self.validate_results(results, *args, **kwargs)

    @staticmethod
    def _get_signature(func):
        sign = inspect.signature(func)
        params = tuple(sign.parameters.keys())
        name = func.__name__ if inspect.isfunction(func) else func.__class__.__name__
        output = {
            UDFBase.DEF_OUTPUT_NAME: UDFBase._get_result_type(
                name, sign.return_annotation
            )
        }
        return params, output

    @staticmethod
    def _get_result_type(func_name, return_annotation):
        if return_annotation is inspect.Signature.empty:
            return UDFBase.DEF_OUTPUT_TYPE
        if return_annotation is str:
            return String
        if return_annotation is int:
            return Int
        raise ValueError(
            f"UDF '{func_name}' output type must be str or int"
            f" while {return_annotation} was provided"
        )

    def _validate_result_type(self, results, *args):
        if not isinstance(results, tuple):
            raise ValueError(
                f"{self.name} returned {type(results)} values"
                f" while tuple was expected. Inputs: {args} Result: {results}"
            )

    def _validate_result_length(self, results, *args):
        out_len = len(self.output)
        res_len = len(results)

        if out_len != res_len:
            raise ValueError(
                f"{self.name} returned {res_len} values"
                f" while {out_len} expected. Inputs: {args} Result: {results}"
            )

    def _validate_result_batch_length(self, results, *args):
        out_len = len(self.output)

        for res in results:
            if not isinstance(res, tuple):
                raise ValueError(
                    f"{self.name} must return a sequence of tuples."
                    f" This may occur if using 'return' instead of 'yield'."
                    f" Inputs: {args} Result: {res}"
                )

            res_len = len(res)
            if out_len != res_len:
                raise ValueError(
                    f"{self.name} returned {res_len} values"
                    f" while {out_len} expected. Inputs: {args} Result: {res}"
                )

    @staticmethod
    def _create_from_func(
        target_class, func: Callable, params=None, output=None, batch=1
    ):
        if not issubclass(target_class, UDFBase):
            raise ValueError(
                f"cannot create UDF from function {func}: "
                f" not supported target class {target_class}"
            )
        sign_params, sign_output = UDFBase._get_signature(func)
        udf = target_class(params or sign_params, output or sign_output, batch=batch)
        udf.process = lambda *args, **kwargs: func(*args, **kwargs)
        return udf


class Mapper(UDFBase):
    def __init__(self, params=None, output=None, batch=1):
        if batch > 1:
            raise ValueError("Mapper does not support batch")

        super().__init__(params, output)

    def validate_results(self, results, *args, **kwargs):
        self._validate_result_type(results, *args)
        self._validate_result_length(results, *args)
        return results

    @staticmethod
    def create_from_func(func, params=None, output=None, batch=1):
        if batch == 1:
            return UDFBase._create_from_func(Mapper, func, params, output)
        else:
            return UDFBase._create_from_func(BatchMapper, func, params, output, batch)


class BatchMapper(Mapper):
    def __init__(self, params=None, output=None, batch=1000):
        if batch == 1:
            raise ValueError(f"{self.name} must be batch UDF")
        UDFBase.__init__(self, params, output, batch)

    def validate_results(self, results, *args, **kwargs):
        # ToDo: this should be done in the level above - together with serialization
        # to not to create the whole copy
        if isinstance(results, types.GeneratorType):
            results = tuple(results)

        self._validate_result_type(results, *args)
        self._validate_result_batch_length(results, *args)
        return results


class Generator(UDFBase):
    def __init__(self, params=None, output=None, batch=1):
        if batch > 1:
            raise ValueError("Generator does not support batch")

        output = output or {}
        super().__init__(params, output={**DatasetRow.schema, **output})

    def validate_results(self, results, *args, **kwargs):
        if isinstance(results, types.GeneratorType):
            results = tuple(results)

        self._validate_result_type(results, *args)
        self._validate_result_batch_length(results, *args)
        return results

    @staticmethod
    def create_from_func(func, params=None, output=None, batch=1):
        return UDFBase._create_from_func(Generator, func, params, output)


class Aggregator(UDFBase):
    def __init__(self, params=None, output=None, batch=1):
        output = output or {}
        super().__init__(params, {**DatasetRow.schema, **output}, batch)

    def validate_results(self, results, *args, **kwargs):
        if isinstance(results, types.GeneratorType):
            for r in results:
                self._validate_result_length(r, *args)
                yield r
            return

        self._validate_result_type(results, *args)
        self._validate_result_batch_length(results, *args)
        return results

    @staticmethod
    def create_from_func(func, params=None, output=None, batch=1):
        return UDFBase._create_from_func(Aggregator, func, params, output, batch)


class GroupMapper(UDFBase):
    def __init__(self, params=None, output=None, batch=1):
        if batch > 1:
            raise ValueError("GroupMapper does not support batch")
        super().__init__(params, output)

    def validate_results(self, results, *args, **kwargs):
        self._validate_result_type(results, *args)
        self._validate_result_length(results, *args)
        return results

    @staticmethod
    def create_from_func(func, params=None, output=None):
        return UDFBase._create_from_func(GroupMapper, func, params, output)
