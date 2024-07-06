GROUP_NAME=matcha
TARGET_GID=$(stat -c "%g" ./)
TARGET_UID=$(stat -c "%u" ./)

echo TARGET_GID $TARGET_GID
echo TARGET_UID $TARGET_UID


if [ $(getent group $GROUP_NAME) ]; then
  PRESENT_GID=$(getent group $GROUP_NAME | cut -d: -f3)
  echo "group $GROUP_NAME exists"
  if [ -ne $TARGET_GID $PRESENT_GID ]; then
    echo "changing its GID (old=$PRESENT_GID, new=$TARGET_GID)"
    groupmod -g $TARGET_GID $GROUP_NAME
  else
    echo "$GROUP_NAME's GID already matches TARGET_GID"
  fi
else
  echo "group $GROUP_NAME does not exist, creating it with GID $TARGET_GID"
  addgroup --gid $TARGET_GID $GROUP_NAME
fi

if [ $(id -u $GROUP_NAME) ]; then
  PRESENT_GID=$(id -u $GROUP_NAME)
  echo "user $GROUP_NAME exists"
  if [ -ne $TARGET_GID $PRESENT_GID ]; then
    echo "changing its GID (old=$PRESENT_GID, new=$TARGET_GID)"
    usermod -g $TARGET_GID $GROUP_NAME
  else
    echo "$GROUP_NAME's GID already matches TARGET_GID"
  fi
else
  echo "user $GROUP_NAME does not exist, creating it with GID $TARGET_GID"
  useradd --uid $TARGET_UID -g $GROUP_NAME -ms /bin/bash $GROUP_NAME
fi

chown -R $GROUP_NAME:$GROUP_NAME /code
chmod -R 755 /tmp

exec su $GROUP_NAME

