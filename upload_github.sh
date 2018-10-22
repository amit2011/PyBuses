#!/usr/bin/env bash

#TODO función para hacer teardown y borrar TEMPDIR al terminar o ante cualquier error

#Cambiar a directorio temporal
TEMPDIR="/tmp/PyBuses_Upload_Github_tmp"
rm -rf "$TEMPDIR"
mkdir "$TEMPDIR"
cd "$TEMPDIR"

#Clonar repo origen, branch public
git clone -b master http://192.168.0.99:10080/david/pybuses.git origin
cd origin

#Obtener last commit
MSG=$(git log -1 --pretty=%B)

#Borrar carpeta git (repo origen)
#rm -r -f .git

#Borrar todas las carpetas y ficheros ocultas (repo origen)
rm -rf .[^.] .??*

# Clonar repo destino
cd ../
git clone -b wip --no-checkout https://github.com/EnforcerZhukov/PyBuses.git destiny

#Copiar archivos origen a destino reemplazando todo
cp -fR origin/* destiny

#Preguntar mensaje del commit
echo "Introduce texto para el commit, o -same para mantener el del repo original:"
read MSGNEW
if [ "$MSGNEW" != "-same" ]
then
    MSG="$MSGNEW"
fi
#echo "Texto del Commit: $MSG"

#Hacer add y commit en destiny
cd destiny || exit 1
git add --all || exit 1
git config user.name "EnforcerZhukov"
#git config user.email "xxx@gmail.com"

git commit -m "$MSG"
#COMPROBAR?? si se ejecutó correctamente con $?
#Devuelve 128 si falta config user.name y user.email de Git; devuelve 0 si se commiteó bien

#Hacer push en destiny (branch wip)
git push -u origin wip

#Borrar directorio temporal
rm -r -f "$TEMPDIR"
