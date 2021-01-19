# CEO-sys AP5 automatic guideline adherence evaluator

## Introduction
Development of a software-based automated evaluation of the adherence to clinical guidelines in the context of the
[CEO-sys - COVID-19 Evidenz-Ökosystems zur Verbesserung von Wissensmanagement und -translation](https://www.netzwerk-universitaetsmedizin.de/projekte/ceo-sys).

## Quickstart

1. Clone repository
   ``` shell
   git clone https://github.com/glichtner/ceosys.git
   ```
2. Install dependencies
   ``` shell
   pip install connexion[swagger-ui]
   ```
3. Run app.py
   ``` shell
   cd ceosys
   python app.py
   ```
4. Visit http://localhost:8088/ui

## Modules

### Machine-readable PICO Statement
* See json files in pico/ folder

### Comparator Engine
```python
raise NotImplementedError()
````

### Visualization
```python
raise NotImplementedError()
````

