from WebUtils.StoppableSleep import StoppableSleep


clock = StoppableSleep()

# CTRL-C should exit the sleep immediately
clock.sleep(5)
print('Done!')

# Can be used multiple times
clock.sleep(5)
print('Done!')
