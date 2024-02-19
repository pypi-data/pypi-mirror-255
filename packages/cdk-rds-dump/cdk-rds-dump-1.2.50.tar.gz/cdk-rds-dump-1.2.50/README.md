# cdk-rds-dump

cdk-rds-dump is a Constructs library for AWS CDK that provides the functionality to dump the contents of Amazon RDS, generate it as an SQL file, and store it in Amazon S3.

![Architecture](./image/architecture.png)

[![View on Construct Hub](https://constructs.dev/badge?package=cdk-rds-dump)](https://constructs.dev/packages/cdk-rds-dump)
[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/badmintoncryer/cdk-rds-dump)
[![npm version](https://badge.fury.io/js/cdk-rds-dump.svg)](https://badge.fury.io/js/cdk-rds-dump)
[![Build Status](https://github.com/badmintoncryer/cdk-rds-dump/actions/workflows/build.yml/badge.svg)](https://github.com/badmintoncryer/cdk-rds-dump/actions/workflows/build.yml)
[![Release Status](https://github.com/badmintoncryer/cdk-rds-dump/actions/workflows/release.yml/badge.svg)](https://github.com/badmintoncryer/cdk-rds-dump/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![npm downloads](https://img.shields.io/npm/dm/cdk-rds-dump.svg?style=flat)](https://www.npmjs.com/package/cdk-rds-dump)

## Usage

Install from npm:

```sh
npm i cdk-rds-dump
```

Then write CDK code as below:

```python
import { RdsDump } from 'cdk-rds-dump';

declare const rdsCluster: rds.DatabaseCluster;
new RdsDump(this, 'MyRdsDump', {
  dbEngine: "mysql",
  rdsCluster: rdsCluster,
  schedule: events.Schedule.cron({ minute: "0", hour: "0" }),
  databaseName: 'myDatabase',
  createSecretsManagerVPCEndpoint: false,
});
```

## How does it work?

This code creates a new RDS cluster and uses the RdsDump Construct to dump the data from that RDS cluster. The dumped data is generated as an SQL file and stored in Amazon S3.

For detailed usage and details of the parameters, refer to the API documentation.

## Why do we need this construct?

AWS RDS is a very useful managed RDB service and includes, by default, the ability to create snapshots.
However, in some cases, such as for development reasons, it is easier to handle SQL files dumped from the DB.
Therefore, cdk-rds-dump was created as a construct to easily create SQL files on a regular basis.

## Contribution

Contributions to the project are welcome. Submit improvement proposals via pull requests or propose new features.

## License

This project is licensed under the Apache-2.0 License.
