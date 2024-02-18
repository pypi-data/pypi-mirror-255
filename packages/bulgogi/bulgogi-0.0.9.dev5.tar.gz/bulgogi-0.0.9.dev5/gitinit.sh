#!/bin/bash 

git submodule init bulgogi 
git submodule update bulgogi

cd bulgogi 
git submodule init libyaml 
git submodule update libyaml
cd ..
