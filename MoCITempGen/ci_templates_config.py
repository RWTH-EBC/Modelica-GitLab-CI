from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDictfrom typing import Optional, Unionimport tomlfrom pathlib import Pathfrom ModelicaPyCI.config import CIConfig, ModelicaPyCIConfigdef write_multiple_rules(rule_list: list = None,                         except_string: str = None,                         rule_option: str = "&&",                         compare_str: str = "!~",                         ci_variable: str = None):    if rule_list is None:        print("Rule is None")        exit(1)    if compare_str == "==":        syntax = '"'    else:        syntax = "/"    if isinstance(rule_list, dict):        if except_string is not None:            _list = []            for var in rule_list:                if var != except_string:                    _list.append(f'{ci_variable}  {compare_str} {syntax}{rule_list[var]}{syntax}')        else:            _list = []            for var in rule_list:                _list.append(f'{ci_variable}  {compare_str} {syntax}{rule_list[var]}{syntax}')        rule_string = ""        for rule in _list:            if rule == _list[0]:                rule_string = f'{rule}  '            else:                rule_string = f'{rule_string} {rule_option} {rule}'        return rule_string    if isinstance(rule_list, list):        if except_string is not None:            rule_list = [f'{ci_variable}  {compare_str} {syntax}{value}{syntax}' for value in rule_list if                         value != except_string]        else:            rule_list = [f'{ci_variable}  {compare_str} {syntax}{value}{syntax}' for value in rule_list]        rule_string = ""        for rule in rule_list:            if rule == rule_list[0]:                rule_string = f'{rule}  '            else:                rule_string = f'{rule_string} {rule_option} {rule}'        return rule_stringclass StageNamesConfig(BaseModel):    check_setting: str = "check_setting"    build_templates: str = "build_templates"    ref_check: str = "Ref_Check"    lib_merge: str = "merge"    html_whitelist: str = "create_html_whitelist"    create_whitelist: str = "create_model_whitelist"    create_example_whitelist: str = "create_example_whitelist"    html_check: str = "HTML_Check"    style_check: str = "Style_check"    dymola_model_check: str = "model_check"    simulate: str = "simulate"    OM_model_check: str = "OM_model_check"    OM_simulate: str = "OM_simulate"    regression_test: str = "RegressionTest"    update_ref: str = "Update_Ref"    plot_ref: str = "plot_ref"    prepare: str = "prepare"    open_PR: str = "open_PR"    update_whitelist: str = "update_whiteList"    build_ci_structure: str = "build_ci_structure"    deploy: str = "deploy"    whitelist_setting: str = "build_ci_whitelist"    class TemplateFilesConfig(BaseModel):    base: Union[str, Path] = ""    regression_file: str = "UnitTests/regression_test.txt"    check_file: str = "UnitTests/check_model.txt"    simulate_file: str = "UnitTests/simulate_model.txt"    page_file: str = "deploy/gitlab_pages.txt"    ibpsa_merge_file: str = "deploy/IBPSA_Merge.txt"    html_file: str = "syntaxtest/html_check.txt"    style_check_file: str = "syntaxtest/style_check.txt"    structure_file: str = "deploy/create_CI_path.txt"    main_yml_file: str = ".gitlab-ci.txt"    setting_file: str = "cleanupscript/ci_setting.txt"    deploy_test_file: str = "deploy/deploy_ci_tests.txt"    build_whitelist_file: str = "cleanupscript/ci_build_whitelist.txt"    OM_check_file: str = "UnitTests/check_OM_model.txt"    OM_simulate_file: str = "UnitTests/simulate_OM_model.txt"    utilities_file: str = "utilities.txt"class CommitInteractionConfig(BaseModel):    update_ref: str = "ci_update_ref"    show_ref: str = "ci_show_ref"    dif_ref: str = "ci_dif_ref"    create_model_wh: str = "ci_create_model_wh"    create_html_wh: str = "ci_create_html_wh"    create_simulate_wh: str = "ci_create_example_wh"    simulate: str = "ci_simulate"    OM_simulate: str = "ci_om_simulate"    check: str = "ci_check"    OM_check: str = "ci_om_check"    regression_test: str = "ci_regression_test"    html: str = "ci_html"    setting: str = "ci_setting"    style: str = "ci_style_check"    trigger_ibpsa: str = "ci_trigger_ibpsa"    merge_except: str = "ci_merge_except"    correct_html: str = "ci_correct_html"    build_structure: str = "ci_build_structure"    build_whitelist_structure: str = "ci_build_whitelist"    reference_check: str = "ci_reference_check"class BotMessageConfig(BaseModel):    merge_commit: str    push_commit: str    create_ref_message: str    update_whitelist_commit: str    create_ref_commit: str    create_CI_template_commit: str    update_model_whitelist_commit: str    update_example_whitelist_commit: str    create_structure_commit: str    create_html_file_commit: str    build_whitelist_commit: strclass WhitelistAndMergeLibraryConfig(BaseModel):    local_path: str = "modelica-ibpsa"    library: str = "IBPSA"    git_url: str = "https://github.com/ibpsa/modelica-ibpsa.git"class GeneralConfig(BaseModel):    # Pydantic setting    model_config = ConfigDict(extra='forbid')    # User inputs    dymola_image: str    open_modelica_image: str    gitlab_page: str    github_repository: str    stage_list: list    packages: dict    library: str    dymola_version: str    conda_environment: str    library_path: Union[str, Path]    # [main_branches]    main_branch: str    ci_config: CIConfig    whitelist_library_config: Optional[WhitelistAndMergeLibraryConfig] = Field(default=None)    # Default parameters    changed_flag: bool = True    extended_examples_flag: bool = True    html_praefix: str = "correct_HTML_"    expire_in_time: str = "7h"    xvfb_flag: str = "xvfb-run -n 77"    bot_name: str = "ebc-aixlib-bot"    utilities_directory: str = "utilities.yml"    template_scripts_dir: str = "scripts"    # TODO: Still required?    buildingspy_upgrade: str = "git+https://github.com/MichaMans/BuildingsPy@testexamplescoverage"    # Default settings for templates, scripts, and CI-names    stage_names: StageNamesConfig = StageNamesConfig()    modelica_py_ci: ModelicaPyCIConfig = ModelicaPyCIConfig()    template_files: TemplateFilesConfig = TemplateFilesConfig()    commit_interaction: CommitInteractionConfig = CommitInteractionConfig()    bot_messages: Optional[BotMessageConfig] = Field(default=None, validate_default=True)    commit_string: Optional[str] = Field(validate_default=True, default=None)    pr_main_branch_rule: Optional[str] = Field(validate_default=True, default=None)    @field_validator("bot_messages")    @classmethod    def create_messages(cls, bot_messages, info: ValidationInfo):        if bot_messages is not None:            return bot_messages        if "whitelist_library_config" in info.data:            whitelist_library_name = info.data['whitelist_library_config'].library        else:            whitelist_library_name = None        whitelist_scripts = info.data["ci_config"].whitelist        return BotMessageConfig(            merge_commit=f"CI message from {info.data['bot_name']}. "                         f"Merge of '{whitelist_library_name}' library. "                         f"Update files {whitelist_scripts.check_file} and {whitelist_scripts.html_file}",            push_commit=f"CI message from {info.data['bot_name']}. "                        f"Automatic push of CI with new regression reference files. "                        f"Please pull the new files before push again.",            create_ref_message=f"CI message from {info.data['bot_name']}. "                               f"New reference files were pushed to this branch. "                               f"The job was successfully and the newly added files are tested in another commit.",            update_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                    f"Update or created new whitelist. "                                    f"Please pull the new whitelist before push again.",            create_ref_commit=f"CI message from {info.data['bot_name']}. "                              f"Automatic push of CI with new regression reference files. "                              f"Please pull the new files before push again. "                              f"Plottet Results $GITLAB_Page/$CI_COMMIT_REF_NAME/charts/",            create_CI_template_commit=f"CI message from {info.data['bot_name']}. "                                      f"Automatic push of CI with new created CI templates. "                                      f"Please pull the new files before push again.",            update_model_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                          f"Update file {whitelist_scripts.check_file}. "                                          f"Please pull the new files before push again.",            update_example_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                            f"Update file {whitelist_scripts.simulate_file}. "                                            f"Please pull the new files before push again.",            create_structure_commit=f"CI message from {info.data['bot_name']}. "                                    f"Add files for ci structure",            create_html_file_commit=f"CI message from {info.data['bot_name']}. "                                    f"Push new files with corrected html Syntax .",            build_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                   f"Push new created whitelists.",        )    @field_validator("bot_messages")    @classmethod    def create_commit_string(cls, commit_string, info: ValidationInfo):        if commit_string is not None:            return commit_string        return write_multiple_rules(            rule_list=list(info.data["commit_interaction"].dict().values()),            rule_option="&&",            compare_str="!~",            ci_variable="$CI_COMMIT_MESSAGE"        )    @field_validator("bot_messages")    @classmethod    def create_pr_main_branch_rule(cls, pr_main_branch_rule, info: ValidationInfo):        if pr_main_branch_rule is not None:            return pr_main_branch_rule        return write_multiple_rules(rule_list=[info.data["main_branch"]],                                    rule_option="||",                                    compare_str="==",                                    ci_variable="$CI_COMMIT_BRANCH")    def to_toml(self, path: Path):        with open(path, "w+") as file:            toml.dump(self.dict(), file)        print(self.dict())    @classmethod    def from_toml(cls, path: Path):        with open(path, "r") as file:            return cls(**toml.load(file))    def get_utilities_path(self):        return self.ci_config.get_dir_path().joinpath(            self.template_scripts_dir, self.utilities_directory        ).as_posix()    @property    def templates_dir(self) -> Path:        return self.ci_config.get_dir_path().joinpath(self.template_scripts_dir)