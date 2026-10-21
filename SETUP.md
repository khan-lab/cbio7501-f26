# Course Setup Guide

**The Art of Reproducible and Open Science**  
*Student software installation and preparation*

This course is hands-on. We will work with a shared research dataset using Python, Git, computational environments, containers, and automated workflows. Please complete the **required setup** before the first practical session and bring your laptop to class.

> **No prior experience with all these tools is expected.** We will learn how to use them during the course. Make sure you are familiar with Linux/Bash.

## 1. Required software

| Tool | Purpose | Installation |
| --- | --- | --- |
| **Git** | Track changes and collaborate on code and documentation | [Install Git](https://git-scm.com/install/) |
| **VS Code** | Edit code and documentation; work in an integrated terminal | [Download VS Code](https://code.visualstudio.com/download) |
| **Miniforge (Conda + Mamba)** | Create environments and install packages, including from Bioconda | [Install Miniforge](https://github.com/conda-forge/miniforge) |
| **Pixi** | Manage reproducible project environments with lock files | [Install Pixi](https://pixi.prefix.dev/latest/installation/) |
| **Quarto** | Create reproducible reports, notebooks, and documents | [Install Quarto](https://quarto.org/docs/get-started/) |
| **GitHub account** | Host repositories, collaborate, and submit course work | [Sign up for GitHub](https://github.com/signup) |
| **Docker Desktop** | Run containerized analyses (used in Week 5) | [Install Docker Desktop](https://www.docker.com/products/docker-desktop/) |

**About Miniforge:** Install **Miniforge**, not a separate Mamba installer. Miniforge includes Conda and Mamba. You do not need the full Anaconda distribution.

**About Docker:** Install Docker Desktop ahead of the container week if supported by your computer. It may require administrator permissions, virtualization support, and (on Windows) WSL 2. If installation is blocked or unsupported, tell the instructor; an alternative environment will be provided where possible. On Linux, Docker Engine may be used instead of Docker Desktop.

## 2. Verify your installation

Open a terminal (or the terminal integrated into VS Code) and run:

```bash
git --version
conda --version
mamba --version
pixi --version
quarto --version
docker --version
```

Each installed tool should report its version. You can also confirm that Docker's engine is running with:

```bash
docker info
```

> `docker --version` verifies the command-line client, **not** that Docker can run containers. `docker info` requires the Docker engine to be running. If Docker is not yet installed, complete that check before Week 5.

If `conda` or `mamba` is not found on Windows, try the **Miniforge Prompt**. On macOS/Linux, reopen the terminal after installation and follow Miniforge's shell-initialization instructions if necessary.

## 3. Tools we will configure later

Please **do not independently install all the workflow tools yet**. We will introduce and configure these in their respective sessions to avoid conflicting installations.

| Tool | Planned use | Resource |
| --- | --- | --- |
| **Snakemake** | Build an automated Python analysis workflow (Week 6) | [Documentation](https://snakemake.readthedocs.io/) |
| **Nextflow** | Explore portable computational workflows (Week 6) | [Website](https://www.nextflow.io/) |
| **nf-core** | Explore community-maintained Nextflow pipelines (Week 6) | [Website](https://nf-co.re/) |
| **Apptainer / Singularity** | Run containers in HPC settings (Week 5) | [Apptainer documentation](https://apptainer.org/docs/) |

## 4. Prepare a small research project

Throughout the course, you will work on **two parallel projects**:

1. **Shared teaching project:** We will use the same dataset and exercises to learn and practice each technique.
2. **Your own research project:** You will apply the techniques to one manageable part of your existing or ongoing computational research.

A good starting point is **one result** that could eventually be reproduced from documented inputs with a single command—not your entire thesis or research pipeline.

## 5. Troubleshooting and support

- **Windows:** Git Bash or the VS Code terminal can be used for Git and basic shell work. Use the Miniforge Prompt for Conda/Mamba if necessary. Docker Desktop may require WSL 2.
- **macOS:** Select installation packages compatible with your Mac's processor (Apple silicon or Intel).
- **Linux:** Use the Linux installation instructions for each tool. Docker Engine is an alternative to Docker Desktop.
- **University-managed laptops:** You may need help with permissions, virtualization, or installing software.

If an installation fails, bring your laptop and the **exact error message** to class. We will do this during the Lab 1.

## 6. Pre-week 2 checklist

- [ ] Git is installed and `git --version` works.
- [ ] VS Code opens successfully.
- [ ] Miniforge is installed and both `conda --version` and `mamba --version` work.
- [ ] Pixi is installed and `pixi --version` works.
- [ ] Quarto is installed and `quarto --version` works.
- [ ] I have a GitHub account and can sign in.
- [ ] Docker is installed, or I have identified an installation issue to resolve before Week 5.
- [ ] I have identified a small research analysis to improve (or will use the course alternative).

**Ready?** Bring your laptop, questions, and curiosity. Our aim is to make computational research easier to understand, rerun, review, and share.
