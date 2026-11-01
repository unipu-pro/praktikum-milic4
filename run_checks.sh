OLLAMA="-e OLLAMA_BASE_URL=http://host.docker.internal:11434"
{
  echo "## docker build --target test"; docker build --target test --progress plain --no-cache -t llm-test . 2>&1 | grep -E "passed|failed"
  echo "## version"; docker run --rm praktikum-llm --version
  echo "## user";    docker run --rm --entrypoint id praktikum-llm
  echo "## status";  docker run --rm $OLLAMA praktikum-llm status 2>&1
  echo "## status (--network host)"
  docker run --rm --network host praktikum-llm status 2>&1
  echo "## stop";    docker run -d -it --name chk $OLLAMA praktikum-llm chat >/dev/null
                     sleep 2
                     ( TIMEFORMAT="stopped in %R s"; time docker stop chk >/dev/null ) 2>&1
                     docker inspect -f 'exit code {{.State.ExitCode}}' chk; docker rm chk >/dev/null
} | tee docker.txt
