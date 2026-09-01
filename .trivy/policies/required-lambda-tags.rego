package user

required_tags := {"team", "environment", "project"}

has_all_required_tags(tags) {
  is_object(tags)
  required_tags <= {k | tags[k]}
}

deny[res] {
  some resource_name
  resource := input.resource.aws_lambda_function[resource_name]
  not has_all_required_tags(resource.tags)

  res := {
    "msg": sprintf("aws_lambda_function '%s' is missing required tags: team, environment, project", [resource_name]),
    "resource": sprintf("aws_lambda_function.%s", [resource_name]),
    "id": sprintf("CUSTOM001-%s", [resource_name]),
  }
}

deny[res] {
  some change_idx
  change := input.resource_changes[change_idx]
  lower(change.type) == "aws_lambda_function"
  not has_all_required_tags(change.change.after.tags)

  res := {
    "msg": sprintf("aws_lambda_function '%s' is missing required tags: team, environment, project", [change.address]),
    "resource": change.address,
    "id": sprintf("CUSTOM001-%s", [change.address]),
  }
}
