# Quickstart

To install dependencies and run the solution you need:

```
pip install -r requirements.txt
source ./run.sh
```

To run the tests

`source ./test.sh`

## Coverage:
```
coverage report

Name                                                   Stmts   Miss  Cover
--------------------------------------------------------------------------
src/app.py                                                10      1    90%
src/repositories/usage_repo.py                            77      6    92%
src/routers/usage.py                                      16      0   100%
src/services/usage_service.py                             90     19    79%
test/conftest.py                                           9      0   100%
test/integration/src/repositories/test_usage_repo.py      28      0   100%
test/src/routers/conftest.py                               7      0   100%
test/src/routers/test_usage.py                            11      0   100%
test/src/services/test_usage_service.py                   38      0   100%
--------------------------------------------------------------------------
```

## Summary of implementation
I have decided to go for a style that is similar to what I was doing for production code.
The architecture is quite simple and is made of 3 parts:
1. the router - The IO interface
2. the service - Applies the business logic of the respository and passes the result to router
3. the repository - Responsible for getting the data

I have decided against sharing models between these layers, not because it wouldn't work here,
but because those kinds of decision usually backfire when the implementation of the model needs to change.

### Testing
For testing I have went for a simple unit + integration pytest setup.
This is quite flexible, especially in combination with dependency injection and starlette app state.
Due to time concerns, I have decided against doing mocks or parallel implementation for the repository.
This fact blurs the line between integration and unit tests as all tests that require Repository will 
make live calls to the instance.


### Nice things
#### Concurrent report gathering
I took this oportunity to show my knowledge of asyncio. In usage_repo.py we can see that the reports are 
gathered in a concurrent manner, giving way better results than a simple sequencial pull. This can still be optimised via httpx stream, but I've found this unnecessary.
#### Use of dependency injection
The choice of using dependency injection on calling 3rd parties is quite important. The main reason I do it by default is that I've found that tests that require 3rd parties are usually the most annoying to have in a CI/CD setting. At some point they will fail. Of course, there are different mocks that you can use at the http or function level (for example httpx_mock), but I've found it cleaner to inject the dependency into the app state on the TestClient level
#### Strong typed implementation
This implementation was made with the strictest pyright setting. It is very close to perfect.


### Misses due to time concerns
1. usage_service should be 2 files
2. the integration testing folder doesn't make sense to exist.
3. I've made some decisions such as the requirements for palindromes to not be empty strings on a whim. It maybe makes sense, but here I would request clarifications.
4. Logging, monitoring, better error handling
5. CI/CD, Static analysis tools, git hooks, etc.
6. More documentation and comments on different functions.
7. Spent more time thinking on what good tests would be in this case. I am quite unhappy with what I have here.


### Conclusion
I believe that this implementation is still pretty strong and with a few tweaks it would do pretty good in a production setting.