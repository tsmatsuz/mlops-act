# act を使用した AML 連携

> このドキュメントは、[MLOps ハンズオン](https://github.com/nohanaga/mlopsv2_handson) における GitHub Workflow (GitHub Actions) を act で実行する手順を記載しています。

あらかじめ、[こちら](https://github.com/nohanaga/mlopsv2_handson/blob/master/Solutions/Solution-Challenge-06-1.md) に記載する手順で service principal を作成しておきます。<br>
(Azure Cloud Shell 上で下記コマンドを実行して、その出力をコピーしておきます。)

```
az ad sp create-for-rbac --name {SERVICE-PRINCIPAL-NAME} --role contributor --scopes /subscriptions/{SUBSCRIPTION-ID}/resourceGroups/{AML-RESOURCE-GROUP-NAME} --sdk-auth
```

ssh でログインするためのターミナルクライアント (任意) を用意します。

Azure 上で、Ubuntu Server LTS 22.04 のリソース (VM) を作成します。

VM にログインします。

> Note : ネットワークに制限のある方は Azure Bastion を使用してください。

下記コマンドを実行して docker のセットアップします。

```
sudo apt-get -y update
sudo apt-get -y install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get -y update
apt-cache policy docker-ce
sudo apt-get -y install docker-ce
sudo usermod -aG docker $USER
```

```docker --help``` と入力してインストールされていることを確認します。


下記コマンドで、act のインストールとパス設定をおこないます。

```
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

設定 (docker と act) を有効にするため、いったんログアウトしてから再度ログインしなおします。

[こちら](https://github.com/nohanaga/mlopsv2_handson/blob/master/Solutions/Solution-Challenge-08-1.md) のドキュメントを見ながら、プロジェクト内に必要なディレクトリ、ファイルを用意します。<br>
これらの構成 (ファイル) は、このリポジトリの project フォルダ内にありますので、コピーしてください。

```
# clone this repo
git clone https://github.com/tsmatsuz/mlops-act
# create project folder
mkdir test
# move to project folder
cd test
# copy all assets in project folder
cp -r ../mlops-act/project/* .
```

下記コマンドを入力して、git repository (上記の ```test``` フォルダ) を初期化します。

```
git init
```

GitHub workflow を作成するため、```test``` 下で、下記コマンドを実行して ```.github/workflows/main.yml``` をエディター (nano) で開きます。

```
mkdir -p .github/workflows
nano .github/workflows/main.yml
```

[ドキュメント](https://github.com/nohanaga/mlopsv2_handson/blob/master/Solutions/Solution-Challenge-08-1.md) で記載している yaml の内容をコピー/ペーストします。

main.yml の steps の先頭に下記タスクを追加してください。

```
- name: Install Az
  run: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

> Note : この設定は、実際の GitHub を使用する際は不要です。(act の場合のみ必要。)<br>
> GitHub 上の ubuntu-latest と docker pull で使用するイメージが異なり、act では az がインストールされていないためです。


ファイルを保存します。

> Note : nano でファイルを保存するには、Ctrl-X キーを実行します。

リポジトリへのファイル登録とコミットをおこないます。

```
git add .
git commit -m "first commit"
```

下記コマンドを実行し、act で GitHub workflow をデバッグ実行します。<br>

```
# move to top folder
cd ..
# run act
act -C test \
  -s AZURE_RESOURCE_GROUP_NAME=[insert resource group name] \
  -s AZURE_ML_WORKSPACE_NAME=[insert workspace name] \
  -s AZURE_CREDENTIALS="`cat <<EOF
[insert credential json]
EOF`"
```

実行例は下記です。

```
act -C test \
  -s AZURE_RESOURCE_GROUP_NAME=TEST20221222-rg \
  -s AZURE_ML_WORKSPACE_NAME=ws1222 \
  -s AZURE_CREDENTIALS="`cat <<EOF
{
  "clientId": "2f5f2ea1-dfb7-40ff-a8c2-de2e62f1a000",
  "clientSecret": "nfc8Q~WYWrZPgNuZv9hMdCsuW2CUpk4meQoXuaTN",
  "subscriptionId": "b3ae1c15-4fef-4362-8c3a-5d804cdeb18d",
  "tenantId": "72f988bf-86f1-41af-91ab-2d7cd011db47",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
EOF`"
```
