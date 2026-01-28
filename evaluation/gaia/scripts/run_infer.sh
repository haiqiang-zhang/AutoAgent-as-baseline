current_dir=$(dirname "$(readlink -f "$0")")

cd $current_dir
cd ../../../
export DOCKER_WORKPLACE_NAME=workplace
export EVAL_MODE=True
export DEBUG=True
export BASE_IMAGES=tjbtech1/gaia-bookworm:amd64
export COMPLETION_MODEL=gpt-4o-mini

python evaluation/gaia/run_infer.py --container_name gaia_lite_eval --model ${COMPLETION_MODEL} --debug --eval_num_workers 1 --port 12345 --data_split validation --level 2023_all --agent_func get_system_triage_agent --git_clone
# python /Users/tangjiabin/Documents/reasoning/metachain/test_gaia_tool.py