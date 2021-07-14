# tensorflow-serving on fargate

## 目的
tf-servingをWebAPIとして提供する

```
cdk deploy
```

cdk deployで
- VPC
- subnet
- ECSクラスタ
- ECSタスク

の作成ができます

その後は
- セキュリティグループを設定
- ALBの設定
- ECSサービスの作成

をしてWebAPIとして使えます

アドレスは
```
ALBのDNS/v1/models/mnist_arcface/
```

samples/
にECRにpushするDockerfileとお試し用のモデル学習のノートブックがあります
お試し用モデルはarcfaceを使ったmnistの分類モデルです


## TODO
- ECRのプライベートリポジトリからのpull([AWS docs](https://docs.aws.amazon.com/ja_jp/AmazonECR/latest/userguide/vpc-endpoints.html#ecr-setting-up-s3-gateway))

	- Fargate(v1.4)では
		- S3ゲートウェイエンドポイント
		- ecr.dkrとecr.apiのエンドポイント

		が必要

- ALB設定とECSサービス設定のコード化

- add requirements


