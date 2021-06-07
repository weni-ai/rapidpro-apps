#!/bin/bash

# Validate if the command he was runned on root of rapidpro-apps

if ! echo $PWD | grep -q $RAPIDPRO_APPS_PATH; then
    echo "You need to be in $RAPIDPRO_APPS_PATH to be able to execute this command!"
    exit 1
fi

function syncproto() {
    app=$1
    echo Copying "$app".proto
    cp "$WENI_PROTO_PATH"/rapidpro_"$app"/$"$app".proto "$RAPIDPRO_APPS_PATH"/weni/"$app"_grpc/grpc_gen/$"$app".proto
}

for app in $(ls weni/ | grep "_grpc" | sed 's/_grpc//g'); do
    syncproto $app

done

echo "   --- Done ---"
