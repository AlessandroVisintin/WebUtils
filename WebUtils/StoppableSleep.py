import signal
from threading import Event


class StoppableSleep:
	"""
	
	Implement a sleep stoppable by KeyboardInterrupt.
	
	"""
	
	
	def __init__(self) -> None:
		"""
		
		Create an event listener.
		Bind function that sets the event to signals.
		
		"""
		
		self.exit = Event()
		signal.signal(signal.SIGINT, self.quit);
	
	
	def quit(self, signum, frame) -> None:
		"""
		
		Set exit flag to True.
		
		"""
		
		self.exit.set()
	
	
	def sleep(self, amount:float) -> None:
		"""
		
		Non-blocking sleep.
		
		Args:
			amount : seconds to sleep. Exit immediately if
				signal is catched
		
		"""
		
		self.exit.clear()
		if amount > 0:
			self.exit.wait(amount)
