# -*- coding: utf-8 -*-

import boto3
import botocore.exceptions
import json
from fnmatch import fnmatch


class TuxPutBucket:
    def __init__(self, json_data):
        self.name = json_data["name"]
        self.root = json_data.get("offset")

    def real_path(self, key):
        if self.root not in [None, "", "/"]:
            return self.root + "/" + key

        return key


class TuxUser:
    def __init__(self, json_data):
        self.token = json_data["token"]
        self.user = json_data["user"]
        self.authorizations = {}

        for a in json_data["authorizations"]:
            bucket = a["bucket"]
            authorizations = a.get("restricted_paths")
            if authorizations is None:
                authorizations = ["*"]

            self.authorizations[bucket] = authorizations

    def path_allowed(self, bucket, key):
        for b_pattern in self.authorizations:
            if fnmatch(bucket, b_pattern):
                for auth_pattern in self.authorizations[b_pattern]:
                    if fnmatch(key, auth_pattern):
                        return True
                # if no match found in auth_patterns, keep going
                # and see if there's another b_pattern match.

        # we have exhaused all bucket patterns and their auth patterns
        # and found no matches.  No auth.
        return False


class s3_server:
    def __init__(self, bucket, region):
        self.bucket = bucket
        self.region = region
        self.client = boto3.client("s3", region_name=region)

    def key_exists(self, key):
        """Try to fetch the metadata for an object. If the object does not
        exist, head_object will raise an exception. Returns True if the
        object exists
        """
        try:
            head = self.client.head_object(Bucket=self.bucket, Key=key)
            if head.get("ContentLength") == 0:
                # Disregard empty objects
                return False
        except (
            botocore.exceptions.ParamValidationError,
            botocore.exceptions.ClientError,
        ):
            return False
        return True

    def create_signed_url(self, key):
        return self.client.generate_presigned_post(
            self.bucket, key, ExpiresIn=90
        )

    def select_from_json(self, expression, key):
        response = self.client.select_object_content(
            Bucket=self.bucket,
            Key=key,
            ExpressionType="SQL",
            Expression=expression,
            InputSerialization={
                "CompressionType": "NONE",
                "JSON": {
                    "Type": "Document",
                },
            },
            OutputSerialization={"JSON": {"RecordDelimiter": "\n"}},
        )

        results = []
        for item in response["Payload"]:
            if "Records" in item:
                record_string = item["Records"]["Payload"].decode("utf-8")
                print("item: %s" % record_string)

                entries = record_string.split("\n")
                valid_entries = []
                for entry in entries:
                    print(" entry - '%s'" % entry)
                    if entry is not None and entry != "":
                        valid_entries.append(entry)

                if len(valid_entries) > 1:
                    record_string = r"[{0}]".format(",".join(valid_entries))
                else:
                    record_string = "\n".join(valid_entries)

                record = json.loads(record_string)
                print("adding record: %s" % record)
                results.append(record)
        return results


# searches the tuxput.json for a bucket entry with the specified name
def verify_bucket(s3_handler, bucket, key):

    # If user doesn't specify a bucket and there's only one bucket
    # in the json file, we return it.  Else, return None and force
    # them to specify one.
    #
    # If they did specify a bucket, then look for it in our json
    if bucket is None:
        exp = """SELECT b.name from S3Object[*].buckets[*] b"""
    else:
        exp = (
            """SELECT * from S3Object[*].buckets[*] b where b.name = '%s'"""
            % bucket
        )
    buckets = s3_handler.select_from_json(exp, key)

    if bucket is None:
        # If and only if one bucket, then return it as defaul
        if len(buckets) == 1:
            return TuxPutBucket(buckets[0])
        # else, return None and force them to pick a bucket
        return None
    else:
        if len(buckets) > 0:
            return TuxPutBucket(buckets.pop())
        else:
            return None


def verify_token(s3_handler, token, key):
    exp = (
        """SELECT * from S3Object[*].users[*] u where u.token = '%s'""" % token
    )
    result = s3_handler.select_from_json(exp, key).pop()
    return TuxUser(result)


def list_buckets(s3_handler, key):
    exp = """SELECT * from S3Object[*].buckets[*] b"""
    results = s3_handler.select_from_json(exp, key)
    return results
