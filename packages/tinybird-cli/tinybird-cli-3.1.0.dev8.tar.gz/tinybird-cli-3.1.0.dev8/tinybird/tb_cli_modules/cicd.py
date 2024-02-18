from dataclasses import dataclass
from enum import Enum
from os import getcwd
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import click
from tornado.template import Template

from tinybird.client import TinyB
from tinybird.feedback_manager import FeedbackManager


class Provider(Enum):
    GitHub = 0
    GitLab = 1


WORKFLOW_VERSION = "v3.0.0"

DEFAULT_REQUIREMENTS_FILE = "tinybird-cli>=3"

GITHUB_CI_YML = """
    ##################################################
    ###   Visit https://github.com/tinybirdco/ci   ###
    ###   for more details or custom CI/CD         ###
    ##################################################

    name: Tinybird - CI Workflow

    on:
      workflow_dispatch:
      pull_request:
        branches:
          - main
          - master
        types: [opened, reopened, labeled, unlabeled, synchronize, closed]{% if data_project_dir != '.' %}
        paths:
          - '{{ data_project_dir }}/**'{% end %}

    concurrency: ${{! github.workflow }}-${{! github.event.pull_request.number }}

    jobs:
        ci: # ci using branches from workspace '{{ workspace_name }}'
          uses: tinybirdco/ci/.github/workflows/ci.yml@{{ workflow_version }}
          with:
            data_project_dir: {{ data_project_dir }}
          secrets:
            tb_admin_token: ${{! secrets.TB_ADMIN_TOKEN }}  # set the Workspace admin token in GitHub secrets
            tb_host: {{ tb_host }}
"""

GITHUB_CD_YML = """
    ##################################################
    ###   Visit https://github.com/tinybirdco/ci   ###
    ###   for more details or custom CI/CD         ###
    ##################################################

    name: Tinybird - CD Workflow

    on:
      workflow_dispatch:
      push:
        branches:
          - main
          - master{% if data_project_dir != '.' %}
        paths:
          - '{{ data_project_dir }}/**'{% end %}
    jobs:
      cd:  # deploy changes to workspace '{{ workspace_name }}'
        uses: tinybirdco/ci/.github/workflows/cd.yml@{{ workflow_version }}
        with:
          data_project_dir: {{ data_project_dir }}
        secrets:
          tb_admin_token: ${{! secrets.TB_ADMIN_TOKEN }}  # set the Workspace admin token in GitHub secrets
          tb_host: {{ tb_host }}
"""

GITHUB_RELEASES_YML = """
    ##################################################
    ###   Visit https://github.com/tinybirdco/ci   ###
    ###   for more details or custom CI/CD         ###
    ##################################################

    name: Tinybird - Releases Workflow

    on:
      workflow_dispatch:
        inputs:
          job_to_run:
            description: 'Select the job to run manually'
            required: true
            default: 'promote'

    jobs:
      cd:  # manage releases for workspace '{{ workspace_name }}'
        uses: tinybirdco/ci/.github/workflows/release.yml@{{ workflow_version }}
        with:
          job_to_run: ${{! inputs.job_to_run }}
          data_project_dir: {{ data_project_dir }}
        secrets:
          tb_admin_token: ${{! secrets.TB_ADMIN_TOKEN }}  # set the Workspace admin token in GitHub secrets
          tb_host: {{ tb_host }}
"""


GITLAB_YML = """
    ##################################################
    ###   Visit https://github.com/tinybirdco/ci   ###
    ###   for more details or custom CI/CD         ###
    ##################################################

    include: "https://raw.githubusercontent.com/tinybirdco/ci/{{ workflow_version }}/.gitlab/ci_cd.yaml"

    .ci_config_rules:
      - &ci_config_rule_deploy
        if: $CI_PIPELINE_SOURCE == "merge_request_event"{% if data_project_dir != '.' %}
        changes:
          - {{ data_project_dir }}/*
          - {{ data_project_dir }}/**/*{% end %}
      - &ci_config_rule_test
        if: $CI_PIPELINE_SOURCE == "merge_request_event"{% if data_project_dir != '.' %}
        changes:
          - {{ data_project_dir }}/*
          - {{ data_project_dir }}/**/*{% end %}

      - &ci_cleanup_rule
        if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH{% if data_project_dir != '.' %}
        changes:
          - {{ data_project_dir }}/*
          - {{ data_project_dir }}/**/*{% end %}

    .cd_config_rules:
      - &cd_config_rule
        if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH{% if data_project_dir != '.' %}
        changes:
          - {{ data_project_dir }}/*
          - {{ data_project_dir }}/**/*{% end %}

    .cicd_variables:
      variables: &cicd_variables
        TB_HOST: "{{ tb_host }}"
        TB_ADMIN_TOKEN: $TB_ADMIN_TOKEN  # set the Workspace admin token in GitLab CI/CD Variables
        DATA_PROJECT_DIR: "{{ data_project_dir }}"

    deploy_ci:  # ci using branches from workspace '{{ workspace_name }}'
      extends: .tb_deploy_ci
      rules:
        - *ci_config_rule_deploy
      variables:
        <<: *cicd_variables

    test_ci:  # ci using branches from workspace '{{ workspace_name }}'
      extends: .tb_test
      needs: ["deploy_ci"]
      rules:
        - *ci_config_rule_test
      variables:
        <<: *cicd_variables

    cleanup_ci_branch:
      extends: .tb_cleanup_ci_branch
      when: always
      rules:
        - *ci_cleanup_rule
      variables:
        <<: *cicd_variables

    deploy_main:  # deploy changes to workspace '{{ workspace_name }}'
      extends: .tb_deploy_main
      rules:
        - *cd_config_rule
      variables:
        <<: *cicd_variables

    run_promote:
      extends: .release_promote
      dependencies: []
      when: manual
      rules:
        - *cd_config_rule
      variables:
        <<: *cicd_variables

    run_rollback:
      extends: .release_rollback
      dependencies: []
      when: manual
      rules:
        - *cd_config_rule
      variables:
        <<: *cicd_variables

    run_rm:
      extends: .release_rm
      dependencies: []
      when: manual
      rules:
        - *cd_config_rule
      variables:
        <<: *cicd_variables

    dry_run_rm_oldest_rollback:
      extends: .dry_run_release_rm_oldest_rollback
      dependencies: []
      when: manual
      rules:
        - *cd_config_rule
      variables:
        <<: *cicd_variables

    run_rm_oldest_rollback:
      extends: .release_rm_oldest_rollback
      dependencies: []
      when: manual
      rules:
        - *cd_config_rule
      variables:
        <<: *cicd_variables


"""


EXEC_TEST_SH = """
#!/usr/bin/env bash
set -euxo pipefail

export TB_VERSION_WARNING=0
export VERSION=$1

run_test() {
    t=$1
    echo "** Running $t **"
    # Check if VERSION is provided
    if [[ -n $VERSION ]]; then
        sed -i "s/tb/tb --semver $VERSION/" $t
    fi
    echo "** $(cat $t)"
    tmpfile=$(mktemp)
    if bash $t $2 >$tmpfile; then
        if diff -B ${t}.result $tmpfile; then
            echo "Test $t: OK";
        else
            echo "🚨 ERROR: Test $t failed, diff:";
            diff -B ${t}.result $tmpfile
            cat $tmpfile
            rm $tmpfile
            return 1
        fi
    else
        echo "🚨 ERROR: Test $t failed with bash command exit code $?"
        cat $tmpfile
        rm $tmpfile
        return 1
    fi
    rm $tmpfile
    echo ""
}
export -f run_test

fail=0
find ./tests -name "*.test" -print0 | xargs -0 -I {} -P 4 bash -c 'run_test "$@"' _ {} $VERSION || fail=1

if [ $fail == 1 ]; then
  exit -1;
fi
"""

APPEND_FIXTURES_SH = """
#!/usr/bin/env bash
set -euxo pipefail

VERSION=$1

directory="datasources/fixtures"
extensions=("csv" "ndjson")

absolute_directory=$(realpath "$directory")

for extension in "${extensions[@]}"; do
  file_list=$(find "$absolute_directory" -type f -name "*.$extension")

  for file_path in $file_list; do
    file_name=$(basename "$file_path")
    file_name_without_extension="${file_name%.*}"

    command="tb --semver $VERSION datasource append $file_name_without_extension datasources/fixtures/$file_name"
    echo $command
    $command
  done
done
"""


@dataclass
class CICDFile:
    template: str
    file_name: str
    dir_path: Optional[str] = None
    warning_message: Optional[str] = None

    @property
    def full_path(self) -> str:
        return f"{self.dir_path}/{self.file_name}" if self.dir_path else self.file_name


class CICDGeneratorBase:
    cicd_files: List[CICDFile] = []

    def __call__(self, path: str, params: Dict[str, Any]):
        for cicd_file in self.cicd_files:
            if cicd_file.dir_path:
                Path(f"{path}/{cicd_file.dir_path}").mkdir(parents=True, exist_ok=True)
            content = Template(cicd_file.template).generate(**params)
            with open(f"{path}/{cicd_file.full_path}", "wb") as f:
                f.write(content)
            click.echo(FeedbackManager.info_cicd_file_generated(file_path=cicd_file.full_path))
            if cicd_file.warning_message is not None:
                return FeedbackManager.warning_for_cicd_file(
                    file_name=cicd_file.file_name, warning_message=cicd_file.warning_message.format(**params)
                )

    def is_already_generated(self, path: str) -> bool:
        for cicd_file in self.cicd_files:
            if Path(f"{path}/{cicd_file.full_path}").exists():
                return True
        return False

    @classmethod
    def build_generator(cls, provider: str) -> Union["GitHubCICDGenerator", "GitLabCICDGenerator"]:
        builder: Dict[str, Union[Type[GitHubCICDGenerator], Type[GitLabCICDGenerator]]] = {
            Provider.GitHub.name: GitHubCICDGenerator,
            Provider.GitLab.name: GitLabCICDGenerator,
        }
        return builder[provider]()


class GitHubCICDGenerator(CICDGeneratorBase):
    cicd_files = [
        CICDFile(template=GITHUB_CI_YML, file_name="tinybird_ci.yml", dir_path=".github/workflows"),
        CICDFile(
            template=GITHUB_CD_YML,
            file_name="tinybird_cd.yml",
            dir_path=".github/workflows",
        ),
        CICDFile(
            template=GITHUB_RELEASES_YML,
            file_name="tinybird_release.yml",
            dir_path=".github/workflows",
            warning_message="Set TB_ADMIN_TOKEN in GitHub secrets. Use the Workspace admin token. Hint: use `tb token copy {token_id}` to copy clipboard",
        ),
    ]


class GitLabCICDGenerator(CICDGeneratorBase):
    cicd_files = [
        CICDFile(
            template=GITLAB_YML,
            file_name=".gitlab-ci.yml",
            warning_message="Set TB_ADMIN_TOKEN in GitLab CI/CD Variables. Use the Workspace admin token. Hint: use `tb token copy {token_id}` to copy clipboard",
        )
    ]


def ask_provider_interactively():
    provider_index = -1
    while provider_index == -1:
        click.echo(FeedbackManager.info_available_git_providers())
        for index, provider in enumerate(Provider):
            click.echo(f"   [{index + 1}] {provider.name}")
        click.echo("   [0] Cancel")

        provider_index = click.prompt("\nUse provider", default=1)

        if provider_index == 0:
            click.echo(FeedbackManager.info_cicd_generation_cancelled_by_user())
            return None

        try:
            return Provider(provider_index - 1).name
        except Exception:
            available_options = ", ".join(map(str, range(1, len(Provider) + 1)))
            click.echo(
                FeedbackManager.error_git_provider_index(host_index=provider_index, available_options=available_options)
            )
            provider_index = -1


async def init_cicd(
    client: TinyB,
    workspace: Dict[str, Any],
    config: Dict[str, Any],
    path: Optional[str] = None,
    data_project_dir: Optional[str] = None,
):
    provider = ask_provider_interactively()
    if provider:
        path = path if path else getcwd()
        data_project_dir = data_project_dir if data_project_dir else "."
        generator = CICDGeneratorBase.build_generator(provider)
        workspace_info = await client.workspace_info()
        token = await client.get_token_by_name("admin token")
        params = {
            "tb_host": client.host,
            "workspace_name": workspace_info["name"],
            "token_name": token["name"],
            "token_id": token["id"],
            "data_project_dir": data_project_dir,
            "workflow_version": WORKFLOW_VERSION,
        }
        warning_message = generator(path, params)
        if warning_message:
            click.echo(warning_message)
        click.echo(FeedbackManager.info_generate_cicd_config(provider=provider))


async def check_cicd_exists(path: Optional[str] = None) -> Optional[Provider]:
    path = path if path else getcwd()
    for provider in Provider:
        generator = CICDGeneratorBase.build_generator(provider.name)
        if generator.is_already_generated(path):
            return provider
    return None
