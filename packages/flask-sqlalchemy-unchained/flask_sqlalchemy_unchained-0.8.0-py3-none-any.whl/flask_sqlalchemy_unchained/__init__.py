import typing as t

from flask import Flask
from flask_sqlalchemy import SQLAlchemy as _FlaskSQLAlchemy
from flask_sqlalchemy.model import Model as _FlaskSQLAlchemyModel
from flask_sqlalchemy.query import Query

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property

from sqlalchemy_unchained import (
    BaseModel as _BaseModel,
    DeclarativeMeta,
    SessionManager,
    ModelManager,
    declarative_base,
    foreign_key,
)


class BaseModel(_BaseModel, _FlaskSQLAlchemyModel):
    pass


class SQLAlchemyUnchained(_FlaskSQLAlchemy):
    def __init__(
        self,
        app=None,
        *,
        metadata=None,
        session_options=None,
        query_class=Query,
        model_class=BaseModel,
        engine_options=None,
        add_models_to_shell=False,
    ):
        super().__init__(
            app,
            metadata=metadata,
            session_options=session_options,
            query_class=query_class,
            model_class=model_class,
            engine_options=engine_options,
            add_models_to_shell=add_models_to_shell,
        )
        self.association_proxy = association_proxy
        self.declared_attr = declared_attr
        self.foreign_key = foreign_key
        self.hybrid_method = hybrid_method
        self.hybrid_property = hybrid_property
        SessionManager.set_session_factory(lambda: self.session())

    def init_app(self, app: Flask) -> None:
        app.config.setdefault("SQLALCHEMY_TRANSACTION_ISOLATION_LEVEL", None)
        super().init_app(app)

    def create_scoped_session(self, options: dict):
        return super()._make_scoped_session(options)

    def _make_declarative_base(
        self,
        model: type[BaseModel] | DeclarativeMeta,  # type: ignore[override]
    ) -> type[t.Any]:
        return super()._make_declarative_base(
            model=declarative_base(
                model=model,  # type: ignore
                metadata=self._make_metadata(None),
            )
        )

    def _apply_driver_defaults(self, options: dict, app: Flask) -> None:
        isolation_level = app.config.get("SQLALCHEMY_TRANSACTION_ISOLATION_LEVEL", None)
        if isolation_level:
            options["isolation_level"] = isolation_level

        super()._apply_driver_defaults(options=options, app=app)
