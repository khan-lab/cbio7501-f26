# containers

Recipes for container images of this project's environment:

- `Dockerfile`: builds an image whose software comes from `pixi.lock`
  (lesson 08), so the container and your laptop cannot drift apart.
- `apptainer.def`: the same for HPC clusters that use Apptainer.
