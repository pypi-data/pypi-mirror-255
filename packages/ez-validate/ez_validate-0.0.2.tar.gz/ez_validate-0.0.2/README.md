# Ez Validate

Simple package for data validation.

# Examples:

## Valid
```
var = 10.0
AssureThat(var).is_float().less_than(12.4).greater_than(9.2)
```

## Invalid
```
var = 5.0
AssureThat(var).is_float().less_than(12.4).greater_than(9.2)
```
This example will raise *ValidationError* with the following message:
> "Untitled var" must be greater than 9.2 but is 5.0

You can change the the name of variable by providing it in *AssureThat* constractor:
```
AssureThat(var, name='Your name').is_float().less_than(12.4).greater_than(9.2)
```
> Your name must be greater than 9.2 but is 5.0

To handle the error use try except clause:
```
try:
	...
except ValidationError as e:
	...
```

## Multiple conditions
**And** condition:
```
AssureThat(var).firts_condition().second_condition().third_condition()
```
**Or** condition:
```
either(
	lambda: AssureThat(var).first_condition(),
	lambda: AssureThat(var).second_condition(),
	lambda: AssureThat(var).third_condition()
)
```
You can make **combination** of **and** and **or** conditions:
```
var = 1.5
either(
	lambda: AssureThat(var).is_float().less_than(3.0).greater_than(0.0),
	lambda: AssureThat(var).is_int().less_than(3).greater_than(0),
	lambda: AssureThat(var).is_none()
)
```
That would mean **var** must be:

 - float **and** greater than 0 **and** less than 3.0
 - **or**
 - int **and** greater than 0 **and** less than 3 
 - **or**
 - None