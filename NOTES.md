# Bug fix: Check availability
## Issue:
At first to verify that the unit is available we were comparing only the check in date which means that another booking can be created for the same unit even though its occupied by another guest. 
## Fix:
The overlap happens when the current check in date is before an existing checkout date AND the current checkout date is after an existing checkout date for the same unit. After catching this overlap we can raise an error.

# Add new feature: user wants to extend his stay. YAAAY!
1. Created a PATCH /api/v1/booking/{id} endpoints that enables the user to extebd their stay by providing the new number of nights.
2. Three validations run before any update happens: verify that the booking exists, validate the number of nights and that it does not conflict with other guests then commit the update.
4. Created unit tests that cover the success path and all edge cases.