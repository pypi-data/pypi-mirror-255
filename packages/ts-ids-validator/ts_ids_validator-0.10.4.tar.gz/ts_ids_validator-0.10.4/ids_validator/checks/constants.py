# we have "root" here, not "root.properties" where field actually located is because we
# are validating only "property" sections, so path would have only "root" in it
from ids_validator.ids_node import NodePath

ROOT_PROPERTIES = NodePath(("root", "properties"))
