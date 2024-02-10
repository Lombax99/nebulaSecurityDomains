import sys
import ruamel.yaml
CS = ruamel.yaml.comments.CommentedSeq

yaml = ruamel.yaml.YAML()

user = CS([{"login":"login1","fullName":"First1 Last1", "list":["a"]},{"login":"login2","fullName":"First2 Last2", "list":["b"]}])
user.yaml_set_comment_before_after_key(1, before='\n')
test = {"category":[{"year":2023,"users":user}]}
yaml.indent(mapping=4, sequence=4, offset=2)
yaml.width = 2048


documents = yaml.dump(test, sys.stdout)
