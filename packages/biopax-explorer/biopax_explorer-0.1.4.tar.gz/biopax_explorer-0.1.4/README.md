# BIOPAX-Explorer 

## Features

A python library for BIOPAX manipulation

BIOPAX-Explorer is a Python package, designed to ease the manipulation of BIOPAX datasets.
It exploits RDF and SPARQL, using a simple object-oriented, domain specific syntax.
Biological Pathway Exchange (BioPAX) is a standard language
that aims to enable integration, exchange, visualization and analysis of biological pathway data.
BioPAX is defined in OWL  and is represented in the RDF/XML format.
using these specifications and formats, BIOPAX-Explorer provides a 100 % compatible object-model
with advanced query features, enabling quick analysis of datasets with a low learning curve. 

##### Documentation
The Python code documentation is available on  [https://fjrmoreews.github.io/biopax-explorer/](https://fjrmoreews.github.io/biopax-explorer/)
 


##### Installation

'
pip install biopax-explorer
'

For large files, use a triple store , do not use the 'direct file in memory' option .
the processing time can be long and a lot of RAM is needed. 

 



### Prerequisites

The package relies mainly on rdfobj, RDFLib and  NetworkX.
Optionnaly you can install  graph-tool for better performances on large graphs  [https://graph-tool.skewed.de/static/doc/quickstart.html](https://graph-tool.skewed.de/static/doc/quickstart.html).


### Source repository


[git repository](https://forgemia.inra.fr/pegase/biopax-explorer)





### Docker installation

#### ready to use Docker container

We provide a easy to use Docker installation,tested with [Docker](https://www.docker.com/) on Linux and [Singularity](https://sylabs.io/)

The  Biopax-Explorer Docker container is available at [https://hub.docker.com/r/fjrmore/biopax_explorer](https://hub.docker.com/r/fjrmore/biopax_explorer)

The container can be used to deploy a jupyter enviroment with  tutorials and example notebooks

A easy way to test Biopax Explorer is to use docker compose :

```
# at the root of the repository
docker-compose up
#the triple store (fuseki) will be available on http://localhost:3030/  (login/password admin/admin)
#Jupyter will be available on http://localhost:8888/  (password : pass)
```

```
#contain of the docker-compose.yml file:

  biopax-explorer:

    image: fjrmore/biopax_explorer

    volumes:
      - ./script/:/work/script
      - ./input:/work/input
    
    links:
      - "db:tstore"
    ports:
      - "8888:8888"
    command: ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root","--NotebookApp.token='pass'" ]


  db:

    image: stain/jena-fuseki:4.0.0
 
    ports:
      - "3030:3030"
    volumes:
      - ./input/:/staging
      - ./db/fuseki:/fuseki
      - ./script/:/script
    environment: 
      - JVM_ARGS=-Xmx5024M
      - ADMIN_PASSWORD=admin


```


### Linux  and Mac installation (Ubuntu and Debian)

```
pip install biopax-explorer

```


###  Windows installation


Installation on windows is possible using at least 2 options :


#### Installation on Windows using Docker-desktop
This procedure has been tested on Windows 10 Enterprise.
first install  Docker-desktop : see https://docs.docker.com/docker-for-windows/install/  

when Docker-desktop is installed, open a power-shell terminal, then entre the followig commands:


*  Biopax-Explorer in Python scripts

```
$vol= (pwd).Path

docker run -p 81:8888 -p 6006:6006 -it  -v ${vol}:/home/user fjrmore/Biopax-Explorer  python3 -c "import Biopax-Explorer; print('package p2g OK')"

curl https://gitlab.inria.fr/fmoreews/Biopax-Explorer/-/raw/master/test/test.py -o test.py
docker run -p 81:8888 -p 6006:6006 -it   -v ${vol}:/home/user fjrmore/Biopax-Explorer   python3 user/test.py

```

```
#create your own script (mycript.py) , go in the directory where your script is located and execute it :.
cd script_dir
$vol= (pwd).Path
docker run -p 81:8888 -p 6006:6006 -it   -v ${vol}:/home/user fjrmore/Biopax-Explorer  python3 mycript.py

```

How to run power-shell : see [this link](https://www.digitalcitizen.life/ways-launch-powershell-windows-admin/)


 *  Biopax-Explorer in jupyter lab
```
$vol= (pwd).Path
docker run -p 81:8888 -p 6006:6006 -it   -v ${vol}:/home/user -e SHOW_PWD=true -e JUPYTER_PWD=password fjrmore/Biopax-Explorer  jupyter.sh
```

then launch a browser and go to the following url : http://localhost:81/lab

and enter the password (password)

#### Installation on Windows using ubuntu terminal 

 See https://www.microsoft.com/en-us/p/ubuntu-2004-lts/9n6svws3rx71?activetab=pivot:overviewtab

After you're environment configuration,
 follow the Docker or Conda + pip installation process (see above).

