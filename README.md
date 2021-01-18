# CEO-sys AP5 automatic guideline adherence evaluator



<img src="docs/img/logo_ceosys.jpg" alt="CEOsys" height="100" />   <img src="docs/img/logo_num.jpg" alt="NUM" height="100" />




## Introduction

Development of a software-based automated evaluation of the adherence to clinical guidelines in the context of the
[CEO-sys - COVID-19 Evidenz-Ökosystems zur Verbesserung von Wissensmanagement und -translation](https://covid-evidenz.de/).

## Requirements
Docker and docker-compose needs to be installed, e.g. under linux via:

```shell
sudo apt install docker docker-compose
```

## Quickstart


1. Clone repository
   ``` shell
   git clone https://github.com/glichtner/ceosys.git
   ```

2. Copy a data sample (not included in this repository)
   ``` shell
   cd ceosys/
   cp <path-to-example-file> data/sample_data_shuffle_large.pkl.gz
   ```

3. Generate secrets and user database
   ``` shell
   ./generate.py
   ```

4. Build docker containers
   ``` shell
   docker-compose build --parallel
   ```

5. Run containers
   ``` shell
   docker-compose up
   ```

5. Visit the dashboard at http://localhost:5000/
