DA = {
    "allow_custom_storage": True,
    "allow_suspend": True,
    "backup_schedule": "40 3 * * *",
    "channel": "stable",
    "crate_version": "5.5.0",
    "dc": {"created": "2023-11-13T02:50:23.313000+00:00", "modified": "2023-11-13T19:15:19.005000+00:00"},
    "deletion_protected": False,
    "external_ip": "20.238.160.167",
    "fqdn": "fuchsia-barriss-offee.aks1.westeurope.azure.cratedb.net.",
    "hardware_specs": {
        "cpus_per_node": 2.0,
        "disk_size_per_node_bytes": 8589934592,
        "disk_type": "standard",
        "disks_per_node": 1,
        "heap_size_bytes": 1073741824,
        "memory_per_node_bytes": 2147483648,
    },
    "health": {"last_seen": "2023-11-13T19:15:19.005000", "running_operation": "", "status": "GREEN"},
    "id": "c4f4bd37-60fa-483e-9e2c-5b3eaacf3b6e",
    "ip_whitelist": None,
    "last_async_operation": {
        "dc": {"created": "2023-11-13T02:50:23.356000+00:00", "modified": "2023-11-13T02:52:38.360000+00:00"},
        "id": "f9a8c977-3b0f-4cc3-a4f1-d418cb39d16c",
        "status": "SUCCEEDED",
        "type": "CREATE",
    },
    "name": "fuchsia-barriss-offee",
    "num_nodes": 1,
    "origin": "cloud",
    "product_name": "crfree",
    "product_tier": "default",
    "product_unit": 0,
    "project_id": "2c6b7c82-d0ab-458c-ae6f-88f8346765ff",
    "subscription_id": "45325e66-5bfc-4cd6-a71b-df59b93cd65c",
    "suspended": False,
    "url": "https://fuchsia-barriss-offee.aks1.westeurope.azure.cratedb.net:4200",
    "username": "admin",
}

D2 = {
    "cluster_id": "c4f4bd37-60fa-483e-9e2c-5b3eaacf3b6e",
    "compression": "gzip",
    "dc": {"created": "2023-11-13T02:52:54.499000+00:00", "modified": "2023-11-13T02:52:54.499000+00:00"},
    "destination": {"create_table": True, "table": "foo"},
    "file": None,
    "format": "csv",
    "id": "e6e64165-4f43-4613-9ab2-344d8af720d2",
    "progress": {
        "bytes": 0,
        "details": {
            "create_table_sql": 'CREATE TABLE "doc"."foo" ("timestamp" TIMESTAMP WITHOUT TIME ZONE,"location" VARCHAR,"temperature" DOUBLE,"humidity" DOUBLE,"wind_speed" DOUBLE)'
        },
        "failed_files": 0,
        "failed_records": 0,
        "message": "Import succeeded",
        "percent": 100.0,
        "processed_files": 1,
        "records": 70000,
        "total_files": 1,
        "total_records": 70000,
    },
    "schema": {"type": "csv"},
    "status": "SUCCEEDED",
    "type": "url",
    "url": {"url": "https://github.com/crate/cratedb-datasets/raw/main/cloud-tutorials/data_weather.csv.gz"},
}



E           docker.errors.DockerException: Credentials store error: StoreError('docker-credential-desktop not installed or not available in PATH')

.venv/lib/python3.11/site-packages/docker/auth.py:278: DockerException

=> rm ~/.docker/config.json
