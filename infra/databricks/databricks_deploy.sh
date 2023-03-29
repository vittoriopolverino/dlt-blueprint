#!/usr/bin/env bash

databricks_authentication() {
  databricks configure --token
}

deploy_clusters() {
  echo -en "\n ------------------------------------------- \n"
  echo -en "\n Deploying databricks clusters . . . \n"

  if [ "${BRANCH_NAME}" == "main" ]
  then
      directory="${WORKING_DIRECTORY}/infra/databricks/clusters/production/*"
  elif [ "${BRANCH_NAME}" == "staging" ]
  then
      directory="${WORKING_DIRECTORY}/infra/databricks/clusters/staging/*"
  else
    echo "ERROR: There is no directory for the branch ${BRANCH_NAME}"
    exit 1
  fi

  echo -en "\n DIRECTORY NAME: ${directory} \n"

  for file in ${directory}
  do
    # read the cluster definition file and store the id in a variable
    cluster_id=$(jq -r '.cluster_id' "$file")

    # check if the cluster id exist
    cmd_response=$(databricks clusters get --cluster-id "$cluster_id")
    echo "${cmd_response}"

    if [[ "${cmd_response}" == *"does not exist"* ]]
    then
      # create the new cluster
      cmd_response=$(databricks clusters create --json-file "$file")
      echo "${cmd_response}"
    else
      # the cluster already exist. Overwrite the existing cluster
      cmd_response=$(databricks clusters edit --json-file "$file")
      echo "${cmd_response}"
    fi

  done
  echo -en "\n ------------------------------------------- \n"
}

deploy_pipelines() {
  echo -en "\n ------------------------------------------- \n"
  echo -en "\n Deploying databricks pipelines . . . \n"

  if [ "${BRANCH_NAME}" == "main" ]
  then
      directory="${WORKING_DIRECTORY}/infra/databricks/pipelines/production/*"
  elif [ "${BRANCH_NAME}" == "staging" ]
  then
      directory="${WORKING_DIRECTORY}/infra/databricks/pipelines/staging/*"
  else
    echo "ERROR: There is no directory for the branch ${BRANCH_NAME}"
    exit 1
  fi
  echo -en "\n DIRECTORY NAME: ${directory} \n"

  for file in ${directory}
  do

    # read the pipeline definition file and store the id in a variable
    pipeline_id=$(jq -r '.id' "$file")
    # read the pipeline definition file and store the name in a variable
    pipeline_name=$(jq -r '.name' "$file")

    # check if the pipeline id exist
    cmd_response=$(databricks pipelines get --pipeline-id "$pipeline_id")
    echo "${cmd_response}"

    if [[ "${cmd_response}" == *"not found"* ]]
    then
      # the pipeline id does not exist, in order to create the new pipeline
      # you need to delete the id key from the file
      jq 'del(.id)' "$file" > tmp.$$.json && mv tmp.$$.json "$file"

      # create the new pipeline
      cmd_response=$(databricks pipelines create --settings "$file")
      echo "${cmd_response}"

      # Get a list of all pipelines using the Databricks CLI and iterate through each pipeline
      pipeline_list=$(databricks pipelines list)
      for pipeline in $(echo "${pipeline_list}" | jq -c '.[]'); do
        # Extract the value of the "name" field from the current pipeline and compare it to the pipeline name from the file
        current_pipeline_name=$(echo "${pipeline}" | jq -r '.name')
        if [[ "${current_pipeline_name}" == "${pipeline_name}" ]]; then
          echo "${cmd_response}"
          # If the pipeline names match, extract the pipeline ID from the current JSON object and add it to the JSON file
          pipeline_id=$(jq -r '.pipeline_id' <<< "${pipeline}")
          echo "pipeline_id: $pipeline_id"
          jq --arg pipeline_id "$pipeline_id" '. + { "id": $pipeline_id }' < "$file" > tmp.$$.json && mv tmp.$$.json "$file"
        fi
      done

      if [[ "${cmd_response}" == *"already exists"* ]]
      then
        # you cannot create the new pipeline because a pipeline withe same name
        # but different id already exist. In order to create the new pipeline
        # update the pipeline file definition with the correct id
        echo -en "\n ERROR: A pipeline with the same name but different id already exist.
        Please update the pipeline file configuration with the correct id \n"
        exit 1
      fi
    else
      # the pipeline already exist. Overwrite the existing pipeline
      cmd_response=$(databricks pipelines edit --settings "$file")
      echo "${cmd_response}"

      if [[ "${cmd_response}" == *"Cannot modify storage location of an existing pipeline"* ]]
      then
        echo -en "\n ERROR: Cannot modify storage location of an existing pipeline \n"
        exit 1
      fi

    fi
  done
  echo -en "\n ------------------------------------------- \n"
}

deploy_jobs() {
  echo -en "\n ------------------------------------------- \n"
  echo -en "\n Deploying databricks jobs . . . \n"

  if [ "${BRANCH_NAME}" == "main" ]
  then
      directory="${WORKING_DIRECTORY}/infra/databricks/jobs/production/*"
  elif [ "${BRANCH_NAME}" == "staging" ]
  then
      directory="${WORKING_DIRECTORY}/infra/databricks/jobs/staging/*"
  else
    echo "ERROR: There is no directory for the branch ${BRANCH_NAME}"
    exit 1
  fi

  echo -en "\n DIRECTORY NAME: ${directory} \n"

  for file in ${directory}
  do
    # read the job definition file and store the id in a variable
    job_id=$(jq -r '.job_id' "$file")
    echo -en "\n JOB_ID=$job_id \n"

    SETTINGS_JSON=$(jq '.settings' "$file")

    # check if the job id exist
    cmd_response=$(databricks jobs get --job-id "$job_id")
    echo "${cmd_response}"

    if [[ "${cmd_response}" == *"does not exist"* ]]
    then
      # create the new job
      cmd_response=$(databricks jobs create --json "$SETTINGS_JSON")
      echo "${cmd_response}"
    else
      # the job already exist. Overwrite the existing job
      cmd_response=$(databricks jobs reset --job-id "$job_id" --json "$SETTINGS_JSON")
      echo "${cmd_response}"
    fi

  done
  echo -en "\n ------------------------------------------- \n"
}

update_repo() {
  echo -en "\n ------------------------------------------- \n"
  echo -en "\n Updating databricks repo to the most recent commit of a ${BRANCH_NAME} remote branch . . . \n"
  # Update a repo to the most recent commit of a remote branch
  echo -en "\n CURRENT_BRANCH=${BRANCH_NAME} \n"
  echo -en "\n DATABRICKS_REPO_ID=${DATABRICKS_REPO_ID} \n"
  databricks repos update --repo-id "${DATABRICKS_REPO_ID}" --branch "${BRANCH_NAME}"
  echo -en "\n ------------------------------------------- \n"
}


deploy_pipelines
update_repo

exit 0

$SHELL
