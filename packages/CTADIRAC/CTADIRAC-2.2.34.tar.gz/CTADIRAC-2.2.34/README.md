# CTADIRAC project

* CTADIRAC is a customized version of the DIRAC interware. As of today, it allows an easy and optimized access to Grid resources (mainly EGI) available to the CTA Virtual Organization (vo.cta.in2p3.fr). When CTAO DPPS will be setup, CTADIRAC will serve as the Computing Ressource and Worflow Management System.
* Follow the [CTADIRAC specific documentation](https://redmine.cta-observatory.org/projects/cta_dirac/wiki/CTA-DIRAC_Users_Guide)
* [Wiki](https://gitlab.cta-observatory.org/cta-computing/dpps/CTADIRAC/-/wikis/)

# Release

* Get `CTADIRAC` on `pypi`: [![PyPI - Version](https://badge.fury.io/py/CTADIRAC.svg)](https://pypi.org/project/CTADIRAC/)

# Deploying CTADIRAC

See the dedicated [server installation documentation](docs/install_CTADIRAC.md).

[CTADIRAC Helm charts](https://gitlab.cta-observatory.org/cta-computing/dpps/workload/CTADIRAC-charts) (in development).

[CTADIRAC fleet deployment](https://gitlab.cta-observatory.org/cta-computing/dpps/workload/ctadirac-deployment) on a Kubernetes cluster.

# Registry

* Install `CTADIRAC`:

```
pip install CTADIRAC
```

* Get `CTADIRAC` client `docker` image:

```
docker pull gitlab.cta-observatory.org:5555/cta-computing/dpps/ctadirac/dirac-client:latest
```

# Contribute to CTADIRAC

* To contribute to CTADIRAC, please check out the full [DIRAC developers guide](http://dirac.readthedocs.io/en/integration/DeveloperGuide/index.html).

* Use [pre-commit](https://pre-commit.com/):
    In your python environment:
    ```bash
    pip install pre-commit
    ```

# Contact Information
* Luisa Arrabito <arrabito@in2p3.fr>
