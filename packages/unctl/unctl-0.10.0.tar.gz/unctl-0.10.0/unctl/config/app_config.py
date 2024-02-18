from pydantic import BaseModel, Field


class Mask(BaseModel):
    name: str
    pattern: str


class Anonymisation(BaseModel):
    masks: list[Mask] = Field(default_factory=list)


class Filter(BaseModel):
    failed_only: bool = Field(default=False)
    checks: list[str] = Field(default_factory=list)
    namespaces: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)


class Interactive(BaseModel):
    prompt: bool = Field(default=True)


class Ignore(BaseModel):
    checks: list[str] = Field(default_factory=list)
    objects: dict[str, list[str]] = Field(default_factory=dict)


class AppConfig(BaseModel):
    anonymisation: Anonymisation = Field(default_factory=Anonymisation)
    filter: Filter = Field(default_factory=Filter)
    interactive: Interactive = Field(default_factory=Interactive)
    ignore: Ignore = Field(default_factory=Ignore)

    def apply_options(self, options):
        if options.no_interactive:
            self.interactive.prompt = False

        if options.failing_only:
            self.filter.failed_only = options.failing_only

        if options.checks and len(options.checks) > 0:
            self.filter.checks = options.checks

        if options.namespaces and len(options.namespaces) > 0:
            self.filter.namespaces = options.namespaces

        if options.categories and len(options.categories) > 0:
            self.filter.categories = options.categories

        if options.services and len(options.services) > 0:
            self.filter.services = options.services

        if options.ignore and len(options.ignore) > 0:
            self.ignore.checks = options.ignore

        if options.ignore_objects and len(options.ignore_objects) > 0:
            self.ignore.objects = {item: [] for item in options.ignore_objects}
