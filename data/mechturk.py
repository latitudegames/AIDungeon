"""
format of tree is
dict {
    tree_id: tree_id_text
    context: context text?
    first_story_block
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
import os


def data_to_forest(filename):

    trees = []
    rows = []

    with open(filename, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    for i in range(1, len(rows[0])):
        tree = {}
        tree["tree_id"] = rows[0][i]
        tree["context"] = rows[1][i]
        tree["first_story_block"] = rows[2][i]
        tree["action_results"] = []
        current_action_results = tree["action_results"]
        row_ind = 3
        while row_ind < len(rows):
            action_result = {}
            action_result["action"] = rows[row_ind][i]
            if row_ind + 1 < len(rows):
                action_result["result"] = rows[row_ind + 1][i]
            else:
                action_result["result"] = None
            action_result["action_results"] = []
            current_action_results.append(action_result)
            current_action_results = action_result["action_results"]
            row_ind += 2
        trees.append(tree)

    return trees


def build_action_samples_helper(context, story_block, action_results, path, tree_id):

    samples = []

    for i, action_result in enumerate(action_results):
        new_path = path[:]
        new_path.append(i)
        if (
            len(action_result["action_results"]) is 0
            and action_result["result"] is not None
        ):
            row = [
                tree_id,
                "".join(str(x) for x in new_path),
                context,
                story_block,
                action_result["action"],
                action_result["result"],
            ]
            samples.append(row)
        else:
            sub_result = build_action_samples_helper(
                context,
                action_result["result"],
                action_result["action_results"],
                new_path,
                tree_id,
            )
            samples += sub_result

    return samples


def make_write_actions_batch(forest, filename):
    # Traverse to the bottom levels of each tree
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(
            file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow(
            [
                "tree_id",
                "path",
                "context",
                "story_block_1",
                "previous_action",
                "story_block_2",
            ]
        )

        for tree in forest:
            first_story_block = tree["first_story_block"]
            samples = build_action_samples_helper(
                tree["context"],
                first_story_block,
                tree["action_results"],
                [],
                tree["tree_id"],
            )

            for sample in samples:
                writer.writerow(sample)


def build_result_samples_helper(
    context, story_block, parent_action_result, path, tree_id
):

    samples = []
    action_results = parent_action_result["action_results"]

    for i, action_result in enumerate(action_results):
        new_path = path[:]
        new_path.append(i)
        if action_result["result"] is None:
            row = [
                tree_id,
                "".join(str(x) for x in new_path),
                context,
                story_block,
                parent_action_result["action"],
                parent_action_result["result"],
                action_result["action"],
            ]
            samples.append(row)
        else:
            sub_result = build_result_samples_helper(
                context,
                parent_action_result["result"],
                action_result,
                new_path,
                tree_id,
            )
            samples += sub_result

    return samples


def make_write_results_batch(forest, filename):

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(
            file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow(
            [
                "tree_id",
                "path",
                "context",
                "story_block_1",
                "previous_action_1",
                "story_block_2",
                "previous_action_2",
            ]
        )

        for tree in forest:
            first_story_block = tree["first_story_block"]
            samples = []
            for i, action_result in enumerate(tree["action_results"]):
                path = [i]
                samples += build_result_samples_helper(
                    tree["context"],
                    first_story_block,
                    action_result,
                    path,
                    tree["tree_id"],
                )

            for sample in samples:
                writer.writerow(sample)


def save_tree(tree, filename):
    with open(filename, "w") as fp:
        json.dump(tree, fp)


def save_forest(forest, forest_name):

    if not os.path.exists("./" + forest_name):
        os.mkdir("./" + forest_name)
    for tree in forest:
        save_tree(tree, "./" + forest_name + "/" + tree["tree_id"] + ".json")


def load_tree(filename):
    with open(filename, "r") as fp:
        tree = json.load(fp)
    return tree


def load_forest(forest_name):

    files = os.listdir("./" + forest_name)
    forest = []
    for file in files:
        forest.append(load_tree("./" + forest_name + "/" + file))
    return forest


def csv_to_dict(file):
    update_dict = {}
    field_names = []

    with open(file, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(update_dict) is 0:
                for item in row:
                    update_dict[item] = []
                    field_names.append(item)

            else:
                for i, item in enumerate(row):
                    update_dict[field_names[i]].append(item)

    return update_dict


def update_forest_with_results(forest_name, update_file):
    update_dict = csv_to_dict(update_file)
    tree_dict = {}
    tree_filenames = os.listdir("./" + forest_name)

    for file_name in tree_filenames:
        tree = load_tree("./" + forest_name + "/" + file_name)
        tree_dict[tree["tree_id"]] = tree

    for i in range(len(update_dict["Input.tree_id"])):
        tree = tree_dict[update_dict["Input.tree_id"][i]]
        current_action_results = tree
        for choice in update_dict["Input.path"][i]:
            choice_num = int(choice)
            current_action_results = current_action_results["action_results"][
                choice_num
            ]

        current_action_results["result"] = update_dict["Answer.result"][i]

    return tree_dict.values()


def update_forest_with_actions(forest_name, update_file):
    update_dict = csv_to_dict(update_file)
    tree_dict = {}
    tree_filenames = os.listdir("./" + forest_name)

    for file_name in tree_filenames:
        tree = load_tree("./" + forest_name + "/" + file_name)
        tree_dict[tree["tree_id"]] = tree

    for i in range(len(update_dict["Input.tree_id"])):
        tree = tree_dict[update_dict["Input.tree_id"][i]]
        current_action_results = tree
        for choice in update_dict["Input.path"][i]:
            choice_num = int(choice)
            current_action_results = current_action_results["action_results"][
                choice_num
            ]

        current_action_results["action_results"].append(
            {
                "action": update_dict["Answer.action_1"][i],
                "result": None,
                "action_results": [],
            }
        )
        current_action_results["action_results"].append(
            {
                "action": update_dict["Answer.action_2"][i],
                "result": None,
                "action_results": [],
            }
        )

    return tree_dict.values()


old_forest_name = "seed_forest_1.8"
new_forest_name = "seed_forest_1.9"
update_type = "results"
update_file = "mech_turk_" + update_type + "5.csv"

if update_type is "results":
    new_forest = update_forest_with_results(old_forest_name, update_file)
    save_forest(new_forest, new_forest_name)
    make_write_actions_batch(new_forest, "actions_batch6.csv")
else:
    new_forest = update_forest_with_actions(old_forest_name, update_file)
    save_forest(new_forest, new_forest_name)
    make_write_results_batch(new_forest, "results_batch5.csv")

print("Done")
