"""
format of tree is
dict {
    tree_id: tree_id_text
    context: context text?
    story_prompt: story_prompt_text
    story_continuation: story_continuation_text
    action_results: [act_res1, act_res2, act_res3...]
}

where each action_result's format is:
dict{
    action: action_text
    result: result_text
    action_results: [act_res1, act_res2, act_res3...]
}
"""

import csv
import json

def get_numeric_cell(cell_string):
    letter = cell_string[0]
    number = cell_string[1:]
    if number.isnumeric():
        col_num = ord(letter.lower()) - 97
        row_num = int(number)
        return row_num, col_num
    else:
        return None


def dungeon_data_to_tree(filename):
    tree = {}
    tree["tree_id"] = filename
    current_action_results = []
    tree["action_results"] = current_action_results
    rows = []

    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for reader_row in reader:
            rows.append(reader_row)

    tree["story_prompt"] = rows[0][1]

    col_ind = 1
    n_columns = len(rows[0])
    while col_ind < n_columns:

        row_and_col = get_numeric_cell(rows[1][col_ind])

        # if it's a cell designation got to traverse tree to find starting point
        if row_and_col is not None:
            cols_to_traverse = [row_and_col[1], col_ind]
            current_action_results = tree["action_results"]
            while cols_to_traverse[0] is not 1:
                new_row_and_col = get_numeric_cell(rows[1][cols_to_traverse[0]])
                cols_to_traverse.insert(0, new_row_and_col[1])

            for j in range(len(cols_to_traverse) -1):
                next_row_and_col = get_numeric_cell(rows[1][cols_to_traverse[j+1]])
                traverse_rows = int((next_row_and_col[0] - 2) / 2)
                for _ in range(traverse_rows):
                    current_action_results = current_action_results[-1]["action_results"]

        else:
            tree["story_continuation"] = rows[1][col_ind]

        ind = 2
        while(ind < len(rows)):

            action_result = {"action": rows[ind][col_ind], "result": None, "action_results": []}
            if ind+1 < len(rows):
                action_result["result"] = rows[ind+1][col_ind]
            current_action_results.append(action_result)
            current_action_results = action_result["action_results"]
            ind += 2

        col_ind += 1

    return tree


def build_action_samples_helper(context, story_block, action_results):

    samples = []

    for action_result in action_results:
        if len(action_result["action_results"]) is 0:
            row = [context, story_block, action_result["action"], action_result["result"]]
            samples.append(row)
        else:
            sub_result = build_action_samples_helper(context, action_result["result"], action_result["action_results"])
            samples += sub_result

    return samples


def make_write_actions_batch(tree, filename):
    # Traverse to the bottom levels of each tree
    with open(filename, mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["context", "story_block_1", "previous_action", "story_block_2"])

        first_story_block = tree["story_prompt"] + tree["story_continuation"]
        samples = build_action_samples_helper(tree["context"], first_story_block, tree["action_results"])

        for sample in samples:
            writer.writerow(sample)


def save_tree(tree, filename):
    with open(filename, 'w') as fp:
        json.dump(tree, fp)

def load_tree(filename):
    with open(filename, 'r') as fp:
        tree = json.load(fp)
    return tree

tree = dungeon_data_to_tree("./data_nick_1.csv")
tree["context"] = "The world has ended. The cities are in ruin and few people are left alive."
make_write_actions_batch(tree, "batch.csv")

save_tree(tree, "tree_data.json")
data = load_tree("tree_data.json")
print("done")
