import copy
import jsonpatch
import json
import luigi
import time


class TransformPatchTask(luigi.Task):
    json_patch_path = luigi.OptionalPathParameter(exists=True)

    def output(self):
        raise NotImplementedError("Task must define output")

    def requires(self):
        raise NotImplementedError("Task must define requires")

    def run(self):
        self.set_status_message("Starting")

        with open(self.json_patch_path) as json_patch_file:
            json_patches = [
                jsonpatch.JsonPatch(patch) for patch in json.load(fp=json_patch_file)
            ]

        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as write_target,
        ):
            self.set_status_message("Count: {current:d}".format(current=0))
            for index, stringified_entity in enumerate(r_input_file):
                entity = json.loads(s=stringified_entity)
                patched_entity = copy.deepcopy(entity)
                for patch in json_patches:
                    try:
                        # `in_place` patches do not allow setting root to None
                        # gwapo patches use an `"add"` operation to filter out patches
                        # so, accumulate the patched entity and check Noneness afterwards
                        patched_entity = patch.apply(patched_entity, in_place=False)
                    except jsonpatch.JsonPatchTestFailed:
                        # each patch begins with a so-called identity test op
                        # it is expected to fail, try the next patch
                        pass
                if patched_entity != None:
                    write_target.write("".join([json.dumps(patched_entity), "\n"]))

            if index % 100 == 0:
                self.set_status_message("Count: {current:d}".format(current=index))
            time.sleep(1 / 5)
