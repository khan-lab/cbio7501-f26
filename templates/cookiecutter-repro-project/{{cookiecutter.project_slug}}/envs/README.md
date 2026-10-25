# envs

Conda environment files for people who do not use Pixi. Generate them from
`pixi.toml` instead of writing them by hand, for example:

    pixi workspace export conda-environment envs/environment.yml

`pixi.toml` and `pixi.lock` stay the source of truth.
