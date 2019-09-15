def generate_cache():
    start_seed = int(sys.argv[1])
    end_seed = int(sys.argv[2])

    # Generate story sections
    prompt_num = 0
    action_queue = []
    prompt = prompts[prompt_num]
    for seed in range(start_seed, end_seed):
        result = retrieve_from_cache(seed, prompt_num, [], "story")
        if result is not None:
            response = result
        else:
            prompt = prompts[prompt_num]
            # print("\n Story prompt is ", prompt)
            response = generate_story_block(prompt)
            # print("\n Story response is ", response)
            cache_file(seed, prompt_num, [], response, "story")

        action_queue.append([seed, 0, [], response])

    while (True):

        next_gen = action_queue.pop(0)
        seed = next_gen[0]
        prompt_num = next_gen[1]
        choices = next_gen[2]
        last_action_result = next_gen[3]

        action_results = retrieve_from_cache(seed, prompt_num, choices, "choices")

        if action_results is not None:
            response = action_results

        else:
            if len(choices) is 0:
                prompt = prompts[prompt_num] + last_action_result
            else:
                prompt = continuing_prompts[prompt_num] + last_action_result
            # print("\n\n Action prompt is \n ", prompt)
            action_results = [generate_action_result(prompt, phrase) for phrase in phrases]
            response = json.dumps(action_results)

            # print("\n\n Action
            cache_file(seed, prompt_num, choices, response, "choices")

        un_jsoned = json.loads(response)
        for j in range(4):
            new_choices = choices[:]
            new_choices.append(j)
            action_queue.append([seed, 0, new_choices, un_jsoned[j][1]])