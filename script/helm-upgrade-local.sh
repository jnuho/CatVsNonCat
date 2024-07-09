#!/bin/bash

helm upgrade tst-release ./tst-chart -f ./tst-chart/values.local.yaml

