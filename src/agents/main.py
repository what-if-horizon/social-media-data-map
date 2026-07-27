import argparse
from initAgents import AgentManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default="configs/models/models.yaml")
    parser.add_argument("--model_dir", default="/gpfs/projects/bsc100/models")
    args = parser.parse_args()

    manager = AgentManager(
    model_config_path=args.models,
    model_dir=args.model_dir)

    messages = [
        {"role": "user", "content": "Say hello in one sentence."}
    ]

    for agent_name in manager.agents.keys():

        print("\n" + "=" * 50)
        print(f"Testing {agent_name}")

        agent = manager.get(agent_name)

        try:
            response = agent.generate(messages)
            print(response[0])

        except Exception as e:
            print(f"ERROR with {agent_name}: {e}")


if __name__ == "__main__":
    main()