#!/bin/bash
sudo docker --help build > tmp_file.txt
grep "Write the image ID to the file" tmp_file.txt
sudo rm tmp_file.txt