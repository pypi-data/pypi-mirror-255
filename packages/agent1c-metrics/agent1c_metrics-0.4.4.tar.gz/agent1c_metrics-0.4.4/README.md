# Agent1C Metrics Service
Service for collecting metrics from 1C service files
Version: 0.4.4

# Installation

## Install package

```
pip install --upgrade agent1c_metrics
```

## Run service

```
python -m agent1c_metrics --reload
```

# Contribution

## Install package in editable mode

```
pip install -e .
```

## Change version (major/minor/patch)

```
bumpver update --patch
```

## Build and publish the package

```
poetry publish --build
```