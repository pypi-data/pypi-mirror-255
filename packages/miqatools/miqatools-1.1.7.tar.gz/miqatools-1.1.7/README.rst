Installing
============

.. code-block:: bash

    pip3 install miqatools --upgrade

Usage
=====

Multi-sample Test Execution

.. code-block:: python

    from miqatools.remoteexecution.triggertestandupload_python import trigger_test_and_upload_by_dsid
    from miqatools.remoteexecution.triggertest_helpers import get_trigger_info

    server_url = "YOURCO.miqa.io"
    trigger_id = "YOUR_TRIGGER_ID"
    api_key = "YOUR_API_KEY"

    # First create the lookup of test result file locations for each dataset:
    ds_id_mapping = get_trigger_info(server_url, trigger_id, api_key=api_key).get("ds_id_mapping", {}).get("results",{}).get("data",{})
    locations_lookup_by_dsid = {ds_id_mapping.get(k):v for k,v in locations_lookup_by_samplename.items()}

    # Use the dataset location lookup and trigger info to kick off "execution" of the trigger, uploading the outputs
    run_id = trigger_test_and_upload_by_dsid(server_url, trigger_id, "YOUR_VERSION_NAME", locations_lookup_by_dsid, filepatterns=["*.vcf"], api_key=api_key)
..

Create and Tag Stand-In Datasets

.. code-block:: python

    from miqatools.datamanagement.datasethelpers import batch_create_datasets_and_tag_or_group

    server_url = "YOURCO.miqa.io"
    trigger_id = "YOUR_TRIGGER_ID"
    api_key = "YOUR_API_KEY"

    batch_create_datasets_and_tag_or_group(server_url, 1, 1, ["Sample1","Sample2"], ["BATCH_1","another_tag"], "BATCH_1", api_key=api_key)
