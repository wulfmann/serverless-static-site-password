import * as cdk from '@aws-cdk/core';
import * as cloudfront from '@aws-cdk/aws-cloudfront';
import * as lambda from '@aws-cdk/aws-lambda';
import * as s3 from '@aws-cdk/aws-s3';
import { join } from 'path';

class Infrastructure extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const s3BucketSource = new s3.Bucket(this, `Bucket`);

        const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, `OAI`);
        s3BucketSource.grantRead(originAccessIdentity);

        const handler = new lambda.Function(this, `Handler`, {
            code: lambda.Code.fromAsset(join(__dirname, 'handler/build')),
            handler: 'main.handler',
            runtime: lambda.Runtime.PYTHON_3_8
        });

        new cloudfront.CloudFrontWebDistribution(this, `Distribution`, {
            originConfigs: [{
                s3OriginSource: {
                    s3BucketSource,
                    originAccessIdentity,
                    originPath: '/current'
                },
                behaviors: [
                    {
                        isDefaultBehavior: true,
                        lambdaFunctionAssociations: [{
                            lambdaFunction: handler.currentVersion,
                            eventType: cloudfront.LambdaEdgeEventType.VIEWER_REQUEST
                        }]
                    },
                    {
                        pathPattern: '/login*'
                    },
                    {
                        pathPattern: '/errors/*'
                    }
                ]
            }],
            errorConfigurations: [{
                errorCode: 404,
                responsePagePath: '/errors/404.html'
            }]
        })
    }
}

const app = new cdk.App();
const appName = 'serverless-static-site-password';
new Infrastructure(app, `${appName}--infrastructure`);
