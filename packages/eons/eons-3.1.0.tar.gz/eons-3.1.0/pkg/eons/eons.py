import logging
import operator
import traceback
import jsonpickle
import inspect
import gc
from copy import deepcopy
import os
import sys
import pkgutil
import importlib.machinery
import importlib.util
import types
import re
from pathlib import Path
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT
import shutil
import dis
import builtins
import argparse
import requests
import importlib
import yaml
from requests_futures.sessions import FuturesSession
from tqdm import tqdm
from zipfile import ZipFile
from eot import EOT

######## START CONTENT ########
def INVALID_NAME():
	return "INVALID_NAME"

class ActualType(type):
	def __repr__(self):
		return self.__name__

class GlobalError(Exception, metaclass=ActualType): pass

class NotInstantiableError(Exception, metaclass=ActualType): pass

class MissingArgumentError(Exception, metaclass=ActualType): pass

class FunctorError(Exception, metaclass=ActualType): pass
class MissingMethodError(FunctorError, metaclass=ActualType): pass
class CommandUnsuccessful(FunctorError, metaclass=ActualType): pass
class InvalidNext(FunctorError, metaclass=ActualType): pass

class ExecutorError(FunctorError, metaclass=ActualType): pass
class ExecutorSetupError(ExecutorError, metaclass=ActualType): pass

class ErrorResolutionError(Exception, metaclass=ActualType): pass
class FailedErrorResolution(ErrorResolutionError, metaclass=ActualType): pass

class SelfRegisteringError(Exception, metaclass=ActualType): pass
class ClassNotFound(SelfRegisteringError, metaclass=ActualType): pass

class HelpWanted(Exception, metaclass=ActualType): pass
class HelpWantedWithRegistering(HelpWanted, metaclass=ActualType): pass

class Fatal(Exception, metaclass=ActualType): pass
class FatalCannotExecute(Fatal, metaclass=ActualType): pass

class PackageError(Exception, metaclass=ActualType): pass

class MethodPendingPopulation(Exception, metaclass=ActualType): pass

class ConstellatusError(Exception, metaclass=ActualType): pass

# util is a namespace for any miscellaneous utilities.
# You cannot create a util.
class util:
	def __init__(this):
		raise NotInstantiableError("util is a namespace, not a class; it cannot be instantiated.")

	#dot.notation access to dictionary attributes
	class DotDict(dict):
		__getattr__ = dict.get
		__setattr__ = dict.__setitem__
		__delattr__ = dict.__delitem__

		def __deepcopy__(this, memo=None):
			return util.DotDict(deepcopy(dict(this), memo=memo))

	# DotDict doesn't pickle right, since it's a class and not a native dict.
	class DotDictPickler(jsonpickle.handlers.BaseHandler):
		def flatten(this, dotdict, data):
			return dict(dotdict)

	@staticmethod
	def RecursiveAttrFunc(func, obj, attrList):
		attr = attrList.pop(0)
		if (not attrList):
			return eval(f"{func}attr(obj, attr)")
		if (not hasattr(obj, attr)):
			raise AttributeError(f"{obj} has not attribute '{attr}'")
		return util.RecursiveAttrFunc(func, getattr(obj, attr), attrList)

	@staticmethod
	def HasAttr(obj, attrStr):
		return util.RecursiveAttrFunc('has', obj, attrStr.split('.'))

	@staticmethod
	def GetAttr(obj, attrStr):
		return util.RecursiveAttrFunc('get', obj, attrStr.split('.'))

	@staticmethod
	def SetAttr(obj, attrStr):
		raise NotImplementedError(f"util.SetAttr has not been implemented yet.")


	@staticmethod
	def LogStack():
		logging.debug(traceback.format_exc())


	class console:

		# Read this (just do it): https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences

		saturationCode = {
			'dark': 3,
			'light': 9
		}

		foregroundCodes = {
			'black': 0,
			'red': 1,
			'green': 2,
			'yellow': 3,
			'blue': 4,
			'magenta': 5,
			'cyan': 6,
			'white': 7
		}

		backgroundCodes = {
			'none': 0,
			'black': 40,
			'red': 41,
			'green': 42,
			'yellow': 43,
			'blue': 44,
			'magenta': 45,
			'cyan': 46,
			'white': 47,
		}

		styleCodes = {
			'none': 0,
			'bold': 1,
			'faint': 2, # Not widely supported.
			'italic': 3, # Not widely supported.
			'underline': 4,
			'blink_slow': 5,
			'blink_fast': 6, # Not widely supported.
			'invert': 7,
			'conceal': 8, # Not widely supported.
			'strikethrough': 9, # Not widely supported.
			'frame': 51,
			'encircle': 52,
			'overline': 53
		}

		@classmethod
		def GetColorCode(cls, foreground, saturation='dark', background='none', styles=None):
			if (styles is None):
				styles = []
			#\x1b may also work.
			compiledCode = f"\033[{cls.saturationCode[saturation]}{cls.foregroundCodes[foreground]}"
			if (background != 'none'):
				compiledCode += f";{cls.backgroundCodes[background]}"
			if (styles):
				compiledCode += ';' + ';'.join([str(cls.styleCodes[s]) for s in list(styles)])
			compiledCode += 'm'
			return compiledCode

		resetStyle = "\033[0m"


	# Add a logging level
	# per: https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/35804945#35804945
	@staticmethod
	def AddLoggingLevel(level, value):
		levelName = level.upper()
		methodName = level.lower()

		if hasattr(logging, levelName):
			raise AttributeError('{} already defined in logging module'.format(levelName))
		if hasattr(logging, methodName):
			raise AttributeError('{} already defined in logging module'.format(methodName))
		if hasattr(logging.getLogger(), methodName):
			raise AttributeError('{} already defined in logger class'.format(methodName))

		# This method was inspired by the answers to Stack Overflow post
		# http://stackoverflow.com/q/2183233/2988730, especially
		# http://stackoverflow.com/a/13638084/2988730
		def logForLevel(this, message, *args, **kwargs):
			if this.isEnabledFor(value):
				this._log(value, message, args, **kwargs)
		def logToRoot(message, *args, **kwargs):
			logging.log(value, message, *args, **kwargs)

		logging.addLevelName(value, levelName)
		setattr(logging, levelName, value)
		setattr(logging.getLogger(), methodName, logForLevel)
		setattr(logging, methodName, logToRoot)

	@staticmethod
	def forerunner(forerunner, *forerunnerArgs, **forerunnerKwargs):
		def WrapperFactory(function):
			def Wrapper(*functionArgs, **functionKwargs):
				forerunner(*forerunnerArgs, **forerunnerKwargs)
				return function(*functionArgs, **functionKwargs)
			return Wrapper
		return WrapperFactory
	

	class BlackMagick:

		@staticmethod
		def InjectIntoModule(source, name, value):
			moduleToHack = inspect.getmodule(source)
			setattr(moduleToHack, name, value)

		# Identify the current function object, without any inputs.
		# TODO: This is slow and implementation dependent. There should be a more optimized way to do this.
		@staticmethod
		def GetCurrentFunction():
			code = inspect.currentframe().f_back.f_code
			functype = type(lambda: None)
			for func in gc.get_referrers(code):
				if type(func) is functype and getattr(func, "__code__", None) is code:
					return func
			return None

jsonpickle.handlers.registry.register(util.DotDict, util.DotDictPickler)


# The Eons way of tracking logical & extensible groupings.
class Namespace:

	def __init__(this, namespaces = None):
		this.namespaces = []

		if (isinstance(namespaces, str)):
			this.namespaces = namespaces.split('/')
			this.namespaces = [namespace for namespace in this.namespaces if len(namespace)]
		elif (isinstance(namespaces, list)):
			this.namespaces = namespaces
		elif (isinstance(namespaces, Namespace)):
			this.namespaces = namespaces.namespaces

	# Get a subset from *this.
	def Slice(this, start=0, end=None):
		return Namespace(this.namespaces[start:end])
	
	def __str__(this):
		ret = ":" + "/".join(this.namespaces)
		if (ret == ":"):
			return ":"
		return ret + "/"

	# Get a namespace string as something more reasonable in python.
	def ToName(this):
		if (not len(this.namespaces)):
			return ""
		return "_".join(this.namespaces) + "_"
	
	def __iadd__(this, other):
		this.namespaces.append(Namespace(other).namespaces)
		return this
	
	def __isub__(this, other):
		this.namespaces = this.namespaces[:-len(Namespace(other).namespaces)]
		return this


class NamespaceTracker:
	def __init__(this):
		# Singletons man...
		if "instance" not in NamespaceTracker.__dict__:
			logging.debug(f"Creating new NamespaceTracker: {this}")
			NamespaceTracker.instance = this
		else:
			return None

		this.last = Namespace()

	@staticmethod
	def Instance():
		if "instance" not in NamespaceTracker.__dict__:
			NamespaceTracker()
		return NamespaceTracker.instance

# Decorator to add a namespace to a class.
# Should look like @namespace(':/foo/bar')
def namespace(ns):
	def DecorateWithNamespace(cls):
		locale = Namespace(ns)
		prepend = locale.ToName()
		NamespaceTracker.Instance().last = locale
		return type(f"{prepend}{cls.__name__}", cls.__bases__, dict(cls.__dict__))
	return DecorateWithNamespace

#Self registration for use with json loading.
#Any class that derives from SelfRegistering can be instantiated with:
#   SelfRegistering("ClassName")
#Based on: https://stackoverflow.com/questions/55973284/how-to-create-this-registering-factory-in-python/55973426
class SelfRegistering(object):

	def __init__(this, *args, **kwargs):
		#ignore args.
		super().__init__()

	@classmethod
	def GetSubclasses(cls):
		for subclass in cls.__subclasses__():
			# logging.info(f"Subclass dict: {subclass.__dict__}")
			yield subclass
			for subclass in subclass.GetSubclasses():
				yield subclass

	@classmethod
	def GetClass(cls, classname):
		for subclass in cls.GetSubclasses():
			if subclass.__name__ == classname:
				return subclass

		# no subclass with matching classname found (and no default defined)
		raise ClassNotFound(f"No known SelfRegistering class: {classname}")			

	#TODO: How do we pass args to the subsequently called __init__()?
	def __new__(cls, classname, *args, **kwargs):
		toNew = cls.GetClass(classname)
		logging.debug(f"Creating new {toNew.__name__} from {toNew.__module__}")

		# Using "object" base class method avoids recursion here.
		child = object.__new__(toNew)

		#__dict__ is always blank during __new__ and only populated by __init__.
		#This is only useful as a negative control.
		# logging.debug(f"Created object of {child.__dict__}")

		return child

	# Registering classes is typically depth-first.
	@staticmethod
	def RegisterAllClassesInDirectory(directory, recurse=True):
		logging.debug(f"Loading SelfRegistering classes in {directory}")
		directoryContents = [i for i in sorted(os.listdir(directory)) if not i.startswith('_')]

		directories = [i for i in directoryContents if os.path.isdir(os.path.join(directory, i))]
		files = [i for i in directoryContents if os.path.isfile(os.path.join(directory, i))]
		files = [f for f in files if f.endswith('.py')]

		if (recurse):
			for dir in directories:				
				SelfRegistering.RegisterAllClassesInDirectory(os.path.join(directory, dir), recurse)

		logging.debug(f"Available modules: {files}")
		for file in files:
			moduleName = file.split('.')[0]

			# logging.debug(f"Attempting to registering classes in {moduleName}.")
			loader = importlib.machinery.SourceFileLoader(moduleName, os.path.join(directory, file))
			module = types.ModuleType(loader.name)
			loader.exec_module(module)

			# Mangle the module name to include the namespace.
			# The namespace is set when exec'ing the module, so we'll reset it after.
			importName = NamespaceTracker.Instance().last.ToName() + moduleName
			NamespaceTracker.Instance().last = Namespace()

			setattr(module, '_source', os.path.join(directory, file))

			# NOTE: the module is not actually imported in that it is available through sys.modules.
			# However, this appears to be enough to get both inheritance and SelfRegistering functionality to work.
			module.__imported_as__ = importName
			sys.modules[importName] = module #But just in case...
			logging.debug(f"{moduleName} imported as {importName}.")

			#### Other Options ####
			# __import__(module)
			# OR
			# for importer, module, _ in pkgutil.iter_modules([directory]):
			#	 importer.find_module(module).exec_module(module) #fails with "AttributeError: 'str' object has no attribute '__name__'"
			#	 importer.find_module(module).load_module(module) #Deprecated

		# enable importing and inheritance for SelfRegistering classes
		if (directory not in sys.path):
			sys.path.append(directory)


# A Datum is a base class for any object-oriented class structure.
# This class is intended to be derived from and added to.
# The members of this class are helpful labels along with the ability to invalidate a datum.
class Datum(SelfRegistering):

	# Don't worry about this.
	# If you really want to know, look at SelfRegistering.
	def __new__(cls, *args, **kwargs):
		return object.__new__(cls)


	def __init__(this, name=INVALID_NAME(), number=0):
		# logging.debug("init Datum")

		# Names are generally useful.
		this.name = name

		# Storing validity as a member makes it easy to generate bad return values (i.e. instead of checking for None) as well as manipulate class (e.g. each analysis step invalidates some class and all invalid class are discarded at the end of analysis).
		this.valid = True

	# Override this if you have your own validity checks.
	def IsValid(this):
		return this.valid == True


	# Sets valid to true
	# Override this if you have members you need to handle with care.
	def MakeValid(this):
		this.valid = True


	# Sets valid to false.
	def Invalidate(this):
		this.valid = False


# A DataContainer allows Data to be stored and worked with.
# This class is intended to be derived from and added to.
# Each DataContainer is comprised of multiple Data (see Datum.py for more).
# NOTE: DataContainers are, themselves Data. Thus, you can nest your child classes however you would like.
class DataContainer(Datum):

	def __init__(this, name=INVALID_NAME()):
		super().__init__(name)

		# The data *this contains.
		this.data = []


	# RETURNS: an empty, invalid Datum.
	def InvalidDatum(this):
		ret = Datum()
		ret.Invalidate()
		return ret


	# Sort things! Requires by be a valid attribute of all Data.
	def SortData(this, by):
		this.data.sort(key=operator.attrgetter(by))


	# Adds a Datum to *this
	def AddDatum(this, datum):
		this.data.append(datum)


	# RETURNS: a Datum with datumAttribute equal to match, an invalid Datum if none found.
	def GetDatumBy(this, datumAttribute, match):
		for d in this.data:
			try: # within for loop 'cause maybe there's an issue with only 1 Datum and the rest are fine.
				if (str(util.GetAttr(d, datumAttribute)) == str(match)):
					return d
			except Exception as e:
				logging.error(f"{this.name} - {e.message}")
				continue
		return this.InvalidDatum()


	# RETURNS: a Datum of the given name, an invalid Datum if none found.
	def GetDatum(this, name):
		return this.GetDatumBy('name', name)


	# Removes all Data in toRem from *this.
	# RETURNS: the Data removed
	def RemoveData(this, toRem):
		# logging.debug(f"Removing {toRem}")
		this.data = [d for d in this.data if d not in toRem]
		return toRem


	# Removes all Data which match toRem along the given attribute
	def RemoveDataBy(this, datumAttribute, toRem):
		toRem = [d for d in this.data if str(util.GetAttr(d, datumAttribute)) in list(map(str, toRem))]
		return this.RemoveData(toRem)


	# Removes all Data in *this except toKeep.
	# RETURNS: the Data removed
	def KeepOnlyData(this, toKeep):
		toRem = [d for d in this.data if d not in toKeep]
		return this.RemoveData(toRem)


	# Removes all Data except those that match toKeep along the given attribute
	# RETURNS: the Data removed
	def KeepOnlyDataBy(this, datumAttribute, toKeep):
		# logging.debug(f"Keeping only class with a {datumAttribute} of {toKeep}")
		# toRem = []
		# for d in this.class:
		#	 shouldRem = False
		#	 for k in toKeep:
		#		 if (str(util.GetAttr(d, datumAttribute)) == str(k)):
		#			 logging.debug(f"found {k} in {d.__dict__}")
		#			 shouldRem = True
		#			 break
		#	 if (shouldRem):
		#		 toRem.append(d)
		#	 else:
		#		 logging.debug(f"{k} not found in {d.__dict__}")
		toRem = [d for d in this.data if str(util.GetAttr(d, datumAttribute)) not in list(map(str, toKeep))]
		return this.RemoveData(toRem)


	# Removes all Data with the name "INVALID NAME"
	# RETURNS: the removed Data
	def RemoveAllUnlabeledData(this):
		toRem = []
		for d in this.data:
			if (d.name =="INVALID NAME"):
				toRem.append(d)
		return this.RemoveData(toRem)


	# Removes all invalid Data
	# RETURNS: the removed Data
	def RemoveAllInvalidData(this):
		toRem = []
		for d in this.data:
			if (not d.IsValid()):
				toRem.append(d)
		return this.RemoveData(toRem)


	# Removes all Data that have an attribute value relative to target.
	# The given relation can be things like operator.le (i.e. <=)
	#   See https://docs.python.org/3/library/operator.html for more info.
	# If ignoreNames is specified, any Data of those names will be ignored.
	# RETURNS: the Data removed
	def RemoveDataRelativeToTarget(this, datumAttribute, relation, target, ignoreNames = []):
		try:
			toRem = []
			for d in this.data:
				if (ignoreNames and d.name in ignoreNames):
					continue
				if (relation(util.GetAttr(d, datumAttribute), target)):
					toRem.append(d)
			return this.RemoveData(toRem)
		except Exception as e:
			logging.error(f"{this.name} - {e.message}")
			return []


	# Removes any Data that have the same datumAttribute as a previous Datum, keeping only the first.
	# RETURNS: The Data removed
	def RemoveDuplicateDataOf(this, datumAttribute):
		toRem = [] # list of Data
		alreadyProcessed = [] # list of strings, not whatever datumAttribute is.
		for d1 in this.data:
			skip = False
			for dp in alreadyProcessed:
				if (str(util.GetAttr(d1, datumAttribute)) == dp):
					skip = True
					break
			if (skip):
				continue
			for d2 in this.data:
				if (d1 is not d2 and str(util.GetAttr(d1, datumAttribute)) == str(util.GetAttr(d2, datumAttribute))):
					logging.info(f"Removing duplicate Datum {d2} with unique id {util.GetAttr(d2, datumAttribute)}")
					toRem.append(d2)
					alreadyProcessed.append(str(util.GetAttr(d1, datumAttribute)))
		return this.RemoveData(toRem)


	# Adds all Data from otherDataContainer to *this.
	# If there are duplicate Data identified by the attribute preventDuplicatesOf, they are removed.
	# RETURNS: the Data removed, if any.
	def ImportDataFrom(this, otherDataContainer, preventDuplicatesOf=None):
		this.data.extend(otherDataContainer.data);
		if (preventDuplicatesOf is not None):
			return this.RemoveDuplicateDataOf(preventDuplicatesOf)
		return []



# BackwardsCompatible classes simply map old names to new names.
# The more compatible an object, the slower it is to access.
# Compatibility can be adjusted by changing the compatibility member variable.
# Compatibility values are versions in accordance with the eons versioning convention: https://eons.llc/convention/versioning
class BackwardsCompatible:

	def __init__(this, compatibility = 2.0):
		# How much backwards compatibility should be maintained.
		# compatibility value is the lowest version of eons that this Functor is compatible with.
		# Compatibility is usually handled in the SupportBackwardsCompatibility method.
		this.compatibility = float(compatibility)

		this.compatibilities = {}

		# Anything that needs to be cached.
		this.cache = util.DotDict()

		# Accelerate backwards compatible lookups.
		# NOTE: this is inverted from this.compatibilities for faster lookup of the new name given the old name.
		this.cache.compatibilities = {}


	# Store a mapping of old names to new names for a particular version.
	def MaintainCompatibilityFor(this, version, compatibilities):
		version = str(version)
		if (version not in this.compatibilities):
			this.compatibilities[version] = {}
		this.compatibilities[version].update(compatibilities)

		this.cache.compatibilities = {}
		for comp in [
			comp
			for ver, comp in this.compatibilities.items()
			if float(ver) <= this.compatibility
		]:
			for new, old in comp.items():
				this.cache.compatibilities[old] = new


	# Support backwards compatibility, to an extent.
	# NOTE: This may cause unwanted type conversions.
	def Get(this, var):
		return eval(f"this.{this.cache.compatibilities[var]}")

# FunctorTracker is a global singleton which keeps a record of all functors that are currently in the call stack.
# Functors should add and remove themselves from this list when they are called.
class FunctorTracker:
	def __init__(this):
		# Singletons man...
		if "instance" not in FunctorTracker.__dict__:
			logging.debug(f"Creating new FunctorTracker: {this}")
			FunctorTracker.instance = this
		else:
			return None

		this.functors = [None]

		this.sequence = util.DotDict()
		this.sequence.current = util.DotDict()
		this.sequence.current.running = False
		this.sequence.current.stage = 0
		this.sequence.stage = []

	@staticmethod
	def Instance():
		if "instance" not in FunctorTracker.__dict__:
			FunctorTracker()
		return FunctorTracker.instance

	@staticmethod
	def Push(functor):
		FunctorTracker.Instance().functors.append(functor)

	# Remove the last instance of the functor from the list.
	@staticmethod
	def Pop(functor):
		tracker = FunctorTracker.Instance()
		tracker.functors.reverse()
		try:
			tracker.functors.remove(functor)
		except:
			pass
		tracker.functors.reverse()

	@staticmethod
	def GetCount():
		return len(FunctorTracker.Instance().functors)


	# Add a sequence to *this.
	@staticmethod
	def InitiateSequence():
		FunctorTracker.Instance().sequence.current.running = True
		FunctorTracker.Instance().sequence.current.stage += 1
		FunctorTracker.Instance().sequence.stage.append(util.DotDict({'state': 'initiated'}))

	# Remove a sequence from *this.
	@staticmethod
	def CompleteSequence():
		if (not FunctorTracker.Instance().sequence.current.running):
			return
		FunctorTracker.Instance().sequence.current.stage -= 1
		FunctorTracker.Instance().sequence.stage.pop()
		FunctorTracker.Instance().sequence.current.running = FunctorTracker.Instance().sequence.current.stage > 0

	
	# Calculate the current namespace, trimming off the last backtrack number of namespaces.
	# The first Functor we Track is likely the Executor, so make sure to skip that.
	@staticmethod
	def GetCurrentNamespace(backtrack=0, start=1):
		return Namespace([functor.name for functor in FunctorTracker.Instance().functors[start:len(FunctorTracker.Instance().functors) - (backtrack+1)]])

	# Get the current namespace as a python usable Functor name.
	@staticmethod
	def GetCurrentNamespaceAsName(backtrack=0, start=1):
		return Namespace.ToName(FunctorTracker.GetCurrentNamespace(start, backtrack))


# ExecutorTracker is a global singleton which keeps a record of all Executors that have been launched.
# This can be abused quite a bit, so please try to restrict usage of this to only:
# * Ease of use global functions
#
# Thanks! 
class ExecutorTracker:
	def __init__(this):
		# Singletons man...
		if "instance" not in ExecutorTracker.__dict__:
			logging.debug(f"Creating new ExecutorTracker: {this}")
			ExecutorTracker.instance = this
		else:
			return None

		this.executors = [None]

	@staticmethod
	def Instance():
		if "instance" not in ExecutorTracker.__dict__:
			ExecutorTracker()
		return ExecutorTracker.instance

	@staticmethod
	def Push(executor):
		ExecutorTracker.Instance().executors.append(executor)

		# Adding the executor to our list here increases its reference count.
		# Executors are supposed to remove themselves from this list when they are deleted.
		# A python object cannot be deleted if it has references.
		# Thus, we forcibly decrease the reference count and rely on Exectuor's self-reporting to avoid accessing deallocated memory.
		# This appears to cause segfaults on some systems, so we'll just live with the fact that Executors will never be destroyed.
		# If you want your executor to stop being tracked, do it yourself. :(
		#
		# ctypes.pythonapi.Py_DecRef(ctypes.py_object(executor))

		logging.debug(f"Now tracking Executor: {executor}")

	@staticmethod
	def Pop(executor):
		try:
			ExecutorTracker.Instance().executors.remove(executor)
			logging.debug(f"No longer tracking Executor: {executor}")
		except:
			pass

	@staticmethod
	def GetLatest():
		return ExecutorTracker.Instance().executors[-1]

#from .Executor import Executor # don't import this, it'll be circular!

# @recoverable
# Decorating another function with this method will engage the error recovery system provided by *this.
# To use this, you must define a GetExecutor() method in your class and decorate the functions you want to recover from.
# For more info, see Executor.ResolveError and the README.md
def recoverable(function):
	def RecoverableDecorator(obj, *args, **kwargs):
		return RecoverableImplementation(obj, obj.GetExecutor(), function, *args, **kwargs)
	return RecoverableDecorator


# This needs to be recursive, so rather than having the recoverable decorator call or decorate itself, we just break the logic into this separate method.
def RecoverableImplementation(obj, executor, function, *args, **kwargs):
	try:
		return function(obj, *args, **kwargs)
	except FailedErrorResolution as fatal:
		raise fatal
	except Exception as e:
		if (not executor.error.resolve):
			raise e
		return Recover(e, obj, executor, function, *args, **kwargs)


def Recover(error, obj, executor, function, *args, **kwargs):
	logging.warning(f"Got error '{error}' from function ({function}) by {obj.name}.")
	util.LogStack()

	# We have to use str(e) instead of pointers to Exception objects because multiple Exceptions will have unique addresses but will still be for the same error, as defined by string comparison.
	if (str(error) not in executor.error.resolution.stack.keys()):
		executor.error.resolution.stack.update({str(error):[]})

	# The executor.error.resolution.stack grows each time we invoke *this or (indirectly) executor.ResolveError().
	# ResolveError is itself @recoverable.
	# So, each time we hit this point, we should also hit a corresponding ClearErrorResolutionStack() call.
	# If we do not, an exception is passed to the caller; if we do, the stack will be cleared upon the last resolution.
	executor.error.depth = executor.error.depth + 1

	if (executor.error.depth > len(executor.error.resolution.stack.keys())+1):
		raise FailedErrorResolution(f"Hit infinite loop trying to resolve errors. Recursion depth: {executor.error.depth}; STACK: {executor.error.resolution.stack}.")

	successfullyRecovered = False
	ret = None
	resolvedBy = None
	for i, res in enumerate(executor.error.resolvers):

		logging.debug(f"Checking if {res} can fix '{error}'.")
		if (not executor.ResolveError(error, i, obj, function)): # attempt to resolve the issue; might cause us to come back here with a new error.
			# if no resolution was attempted, there's no need to re-run the function.
			continue
		try:
			logging.debug(f"Trying function ({function}) again after applying {res}.")
			resolvedBy = res
			ret = function(obj, *args, **kwargs)
			successfullyRecovered = True
			break

		except Exception as e2:
			if (str(error) == str(e2)):
				logging.debug(f"{res} failed with '{e2}'; will ignore and see if we can use another ErrorResolution to resolve '{error}'.")
				# Resolution failed. That's okay. Let's try the next.
				# Not all ErrorResolutions will apply to all errors, so we may have to try a few before we get one that works.
				continue
			else:
				# The error changed, maybe we're making progress.
				ret = Recover(e2, obj, executor, function, *args, **kwargs)
				successfullyRecovered = True
				break

	if (successfullyRecovered):
		executor.ClearErrorResolutionStack(str(error)) # success!
		logging.recovery(f"{resolvedBy} successfully resolved '{error}'!")
		logging.debug(f"Error stack is now: {executor.error.resolution.stack}")
		return ret

	#  We failed to resolve the error. Die
	sys.tracebacklimit = 0 # traceback is NOT helpful here.
	raise FailedErrorResolution(f"Tried and failed to resolve: {error} STACK: {executor.error.resolution.stack}. See earlier logs (in debug) for traceback.")


# Don't import Method or Executor, even though they are required: it will cause a circular dependency.
# Instead, pretend there's a forward declaration here and don't think too hard about it ;)
################################################################################

# Functor is a base class for any function-oriented class structure or operation.
# This class derives from Datum, primarily, to give it a name but also to allow it to be stored and manipulated, should you so desire.
# Functors will automatically Fetch any ...Args specified.
# You may additionally specify required methods (per @method()) and required programs (i.e. external binaries).
# When Executing a Functor, you can say 'next=[...]', in which case multiple Functors will be Executed in sequence. This is necessary for the method propagation machinery to work.
# When invoking a sequence of Functors, only the result of the last Functor to be Executed or the first Functor to fail will be returned.
class Functor(Datum, BackwardsCompatible):

	# Which function should be overridden when creating a @kind from *this.
	primaryFunctionName = 'Function'

	def __init__(this, name=INVALID_NAME()):
		Datum.__init__(this, name)
		BackwardsCompatible.__init__(this)

		# All @methods.
		# See Method.py for details.
		# NOTE: Functor cannot have @methods, since it would create a circular dependency. However, all downstream children of Functor may.
		this.methods = {}

		# Settings for the methods of *this
		this.method = util.DotDict()

		# Which method to call when executing *this through __call__.
		this.method.function = 'Function'
		this.method.rollback = 'Rollback'
		
		# You probably don't need to change this.
		# Similar to fetchFrom, methodSources lists where methods should be populated from and in what order
		# Each entry is a key-value pair representing the accessible member (member's members okay) and whether or not to honor Method.propagate.
		# If the value is False, all methods will be added to *this.methods and will overwrite any existing methods. Otherwise, only methods with propagate == True will be added and combined with existing methods. When in doubt, prefer True.
		this.method.sources = {
			'classMethods': False, # classMethods is created when a class uses @method()s
			'precursor.methods': True
		}

		# Specify any methods / member functions you need here.
		# *this will not be invoked unless these methods have been provided by a precursor.
		this.method.required = []

		# Internal var indicating whether or not Initialize has been called.
		this.initialized = False

		# The arguments provided to *this.
		this.args = []
		this.kwargs = {}

		# The arguments *this takes.
		this.arg = util.DotDict()
		this.arg.kw = util.DotDict()

		# All necessary args that *this cannot function without.
		this.arg.kw.required = []

		# Static arguments are Fetched when *this is first called and never again.
		# All static arguments are required.
		this.arg.kw.static = []

		# Mark args that meet the given requirements as valid.
		# For now, only static args require a member variable.
		this.arg.valid = util.DotDict()
		this.arg.valid.static = False

		# Because values can be Fetched from *this, values that should be provided in arguments will be ignored in favor of those Fetched by a previous call to *this.
		# Thus, we can't enable 'this' when Fetching required or optional KWArgs (this is done for you in ValidateArgs)
		# If you want an arg to be populated by a child's member, make it static.

		# For optional args, supply the arg name as well as a default value.
		this.arg.kw.optional = {}

		# Instead of taking ...Args and ...KWArgs, we only take KWArgs.
		# You can list ordered arguments here which will correspond with either required or optional KWArgs.
		# If the arg you specify here does not exist in ...KWArgs, an error will be thrown.
		# Use this to make calling your Functor easier (e.g. MyMethod('some value') vs MyMethod(my_value='some value'))
		this.arg.mapping = []

		# If you'd like to enforce types on your arguments, rather than use Python autotyping, specify the {'argName': type} pairs here.
		this.arg.type = {}

		# Settings for dependency injection.
		this.fetch = util.DotDict()

		# Default places to Fetch from.
		# Add to this list when extending Fetch().
		# Remove from this list to restrict Fetching behavior.
		# Reorder this list to make Fetch more efficient for your use case.
		# Also see FetchWith and FetchWithout for ease-of-use methods.
		this.fetch.use = [
			'this',
			'args',
			'globals',
			'config', #local (if applicable) or per Executor; should be before 'executor' if using a local config.
			'epidef',
			'precursor',
			'caller',
			'executor',
			'environment',
		]

		# Fetch is modular.
		# You can add your own {'from':this.customSearchMethod} pairs to fetchLocations by overriding PopulateFetchLocations().
		# Alternatively, you may add to fetchLocations automatically by adding a fetchFrom entry and defining a method called f"fetch_location_{your new fetchFrom entry}(this, varName, default)".
		# The order of fetchLocations does not matter; the order of each fetchFrom provided to Fetch() does. This allows users to set their preferred search order for maximum efficiency.
		this.fetch.locations = {}

		# System executables that *this depends on.
		this.program = util.DotDict()

		# All external dependencies *this relies on (binaries that can be found in PATH).
		# These are treated as static args (see above).
		this.program.required = []

		# New style overrides.
		this.override = util.DotDict()
		this.override.config = {}

		# Feature flags.
		# What can *this do?
		this.feature = util.DotDict()
		
		# Automatically return this.
		# Also enables partial function calls.
		this.feature.autoReturn = True

		# Rolling back can be disabled by setting this to False.
		this.feature.rollback = True

		# Whether or not we should pass on exceptions when calls fail.
		this.feature.raiseExceptions = True

		# Whether or not to utilize arg.mapping
		# Set to False if you want to capture args as variadic, etc.
		this.feature.mapArgs = True

		# Allow partial function calls by marking *this as incomplete.
		# Incomplete means that more arguments need to be provided.
		this.incomplete= False

		# this.result encompasses the return value of *this.
		# The code is a numerical result indication the success or failure of *this and is set automatically.
		# 0 is success; 1 is no change; higher numbers are some kind of error.
		# this.result.data should be set manually.
		# It is highly recommended that you check result.data in DidFunctionSucceed().
		this.result = util.DotDict()
		this.result.code = 0
		this.result.data = util.DotDict()

		# Ease of use members
		# These can be calculated in Function and Rollback, respectively.
		# Assume success to reduce the overhead of creating small Functors.
		this.functionSucceeded = True
		this.rollbackSucceeded = True

		# That which came before.
		this.precursor = None

		# The reason *this is being __call__()ed.
		# i.e. the previous Functor in the call stack.
		this.caller = None

		# The object to which this belongs.
		# epidef as in "above definition"
		# For example, if *this is a method of another Functor, this.upper would refer to that other Functor.
		this.epidef = None

		# The overarching program manager.
		this.executor = None

		# Those which come next (in order).
		this.next = []

		# Callback method
		this.callback = util.DotDict()
		this.callback.fetch = None

		this.abort = util.DotDict()
		this.abort.WarmUp = False

		this.cloning = util.DotDict()
		this.cloning.exclusions = [
			'executor',
			'precursor',
			'epidef',
			'caller',
			'next',
			'callback',
		]

		# Mappings to support older versions
		this.MaintainCompatibilityFor(2.0, {
			'method.call': 'callMethod',
			'method.rollback': 'rollbackMethod',
			'method.sources': 'methodSources',
			'method.required': 'requiredMethods',
			'arg.kw.required': 'requiredKWArgs',
			'arg.kw.optional': 'optionalKWArgs',
			'arg.kw.static': 'staticKWArgs',
			'arg.valid.static': 'staticArgsValid',
			'arg.mapping': 'argMapping',
			'fetch.use': 'fetchFrom',
			'fetch.locations': 'fetchLocations',
			'program.required': 'requiredPrograms',
			'override.config': 'configNameOverrides',
			'feature.autoReturn': 'enableAutoReturn',
			'feature.rollback': 'enableRollback',
			'feature.raiseExceptions': 'raiseExceptions',
		})


	# Override this and do whatever!
	# This is purposefully vague.
	def Function(this):
		pass


	# Undo any changes made by Function.
	# Please override this too!
	def Rollback(this):
		pass


	# Return whether or not Function was successful.
	# Override this to perform whatever success and failure checks are necessary.
	def DidFunctionSucceed(this):
		return this.functionSucceeded


	# RETURN whether or not the Rollback was successful.
	# Override this to perform whatever success and failure checks are necessary.
	def DidRollbackSucceed(this):
		return this.rollbackSucceeded


	# Grab any known and necessary args from this.kwargs before any Fetch calls are made.
	def ParseInitialArgs(this):
		pass


	# Override this with any logic you'd like to run at the top of __call__
	def BeforeFunction(this):
		pass


	# Override this with any logic you'd like to run at the bottom of __call__
	def AfterFunction(this):
		pass


	# Override this with any logic you'd like to run at the top of __call__
	def BeforeRollback(this):
		pass


	# Override this with any logic you'd like to run at the bottom of __call__
	def AfterRollback(this):
		pass


	# Called during initialization.
	# Use this to address any type conversion, etc.
	def SupportBackwardsCompatibility(this):
		pass


	# Create a list of methods / member functions which will search different places for a variable.
	# See the end of the file for examples of these methods.
	def PopulateFetchLocations(this):
		try:
			for loc in this.fetch.use:
				this.fetch.locations.update({loc:getattr(this,f"fetch_location_{loc}")})
		except:
			# If the user didn't define fetch_location_{loc}(), that's okay. No need to complain
			pass


	# Convert Fetched values to their proper type.
	# This can also allow for use of {this.val} expression evaluation.
	# If evaluateExpressions is True, this will automatically evaluate any strings containing {} expressions.
	def EvaluateToType(this, value, evaluateExpressions=True):
		if (value is None or value == "None"):
			return None

		if (isinstance(value, (bool, int, float))):
			return value

		if (isinstance(value, dict)):
			ret = util.DotDict()
			for key, val in value.items():
				ret[key] = this.EvaluateToType(val, evaluateExpressions)
			return ret

		if (isinstance(value, list)):
			ret = []
			for val in value:
				ret.append(this.EvaluateToType(val, evaluateExpressions))
			return ret

		if (isinstance(value, str)):
			# Automatically determine if the string is an expression.
			# If it is, evaluate it.
			if (evaluateExpressions and ('{' in value and '}' in value)):
				evaluatedValue = eval(f"f\"{value}\"")
			else:
				evaluatedValue = value

			# Check resulting type and return a casted value.
			# TODO: is there a better way than double cast + comparison?
			if (evaluatedValue.lower() == "false"):
				return False
			elif (evaluatedValue.lower() == "true"):
				return True

			try:
				if (str(float(evaluatedValue)) == evaluatedValue):
					return float(evaluatedValue)
			except:
				pass

			try:
				if (str(int(evaluatedValue)) == evaluatedValue):
					return int(evaluatedValue)
			except:
				pass

			# The type must be a plain-old string.
			return evaluatedValue

		# Meh. Who knows?
		return value


	# Wrapper around setattr
	def Set(this, varName, value, evaluateExpressions=True):
		for key, var in this.override.config.items():
			if (varName == key):
				varName = var
				break
		if (varName in this.arg.type.keys()):
			cls = this.arg.type[varName]
			if (not inspect.isclass(cls) and isinstance(cls, object)):
				cls = cls.__class__
			if (issubclass(cls, Functor)):
				value = cls(value=value)
			else:
				value = cls(value)
		else:
			value = this.EvaluateToType(value, evaluateExpressions)

		logging.info(f"{varName} = {value} ({type(value)})")
		exec(f"this.{varName} = value")


	# Will try to get a value for the given varName from:
	#	first: this
	#	second: whatever was called before *this
	#	third: the executor (args > config > environment)
	# RETURNS:
	#   When starting: the value of the given variable or default
	#   When not starting (i.e. when called from another Fetch() call): a tuple containing either the value of the given variable or default and a boolean indicating if the given value is the default or if the Fetch was successful.
	# The attempted argument will keep track of where we've looked so that we don't enter any cycles. Attempted implies not start.
	def Fetch(this, varName, default=None, fetchFrom=None, start=True, attempted=None):
		if (attempted is None):
			attempted = []

		if (this in attempted):
			logging.debug(f"...{this} detected loop ({attempted}) while trying to fetch {varName}; using default: {default}.")
			if (start):
				return default
			else:
				return default, False

		attempted.append(this)

		if (fetchFrom is None):
			fetchFrom = this.fetch.use

		if (start):
			logging.debug(f"Fetching {varName} from {fetchFrom}...")

		for loc in fetchFrom:
			if (loc not in this.fetch.locations.keys()):
				# Maybe the location is meant for executor, precursor, etc.
				continue

			ret, found = this.fetch.locations[loc](varName, default, fetchFrom, attempted)
			if (found):
				logging.debug(f"...{this.name} got {varName} from {loc}.")
				if (this.callback.fetch):
					this.callback.fetch(varName = varName, location = loc, value = ret)
				if (start):
					return ret
				return ret, True

		if (this.callback.fetch):
			this.callback.fetch(varName = varName, location = 'default', value = default)

		if (start):
			logging.debug(f"...{this.name} could not find {varName}; using default: {default}.")
			return default
		else:
			return default, False


	# Ease of use method for Fetching while including certain search locations.
	def FetchWith(this, doFetchFrom, varName, default=None, currentFetchFrom=None, start=True, attempted=None):
		if (currentFetchFrom is None):
			currentFetchFrom = this.fetch.use
		fetchFrom = list(set(currentFetchFrom + doFetchFrom))
		return this.Fetch(varName, default, fetchFrom, start, attempted)

	# Ease of use method for Fetching while excluding certain search locations.
	def FetchWithout(this, dontFetchFrom, varName, default=None, currentFetchFrom=None, start=True, attempted=None):
		if (currentFetchFrom is None):
			currentFetchFrom = this.fetch.use
		fetchFrom = [f for f in this.fetch.use if f not in dontFetchFrom]
		return this.Fetch(varName, default, fetchFrom, start, attempted)

	# Ease of use method for Fetching while including some search location and excluding others.
	def FetchWithAndWithout(this, doFetchFrom, dontFetchFrom, varName, default=None, currentFetchFrom=None, start=True, attempted=None):
		if (currentFetchFrom is None):
			currentFetchFrom = this.fetch.use
		fetchFrom = [f for f in this.fetch.use if f not in dontFetchFrom]
		fetchFrom = list(set(fetchFrom + doFetchFrom))
		return this.Fetch(varName, default, fetchFrom, start, attempted)


	# Make sure arguments are not duplicated.
	# This prefers optional args to required args.
	def RemoveDuplicateArgs(this):
		deduplicate = [
			'arg.kw.required',
			'method.required',
			'program.required'
		]
		for dedup in deduplicate:
			exec(f"this.{dedup} = list(dict.fromkeys(this.{dedup}))")

		for arg in this.arg.kw.required:
			if (arg in this.arg.kw.optional.keys()):
				logging.warning(f"Making required kwarg optional to remove duplicate: {arg}")
				this.arg.kw.required.remove(arg)


	# Populate all static details of *this.
	def Initialize(this):
		if (this.initialized):
			return
		
		this.SupportBackwardsCompatibility()

		this.PopulateFetchLocations()
		this.RemoveDuplicateArgs()

		for prog in this.program.required:
			if (shutil.which(prog) is None):
				raise FunctorError(f"{prog} required but not found in path.")

		this.initialized = True

	# Make sure all static args are valid.
	def ValidateStaticArgs(this):
		if (this.arg.valid.static):
			return

		for skw in this.arg.kw.static:
			if (util.HasAttr(this, skw)): # only in the case of children.
				continue

			fetched = this.Fetch(skw)
			if (fetched is not None):
				this.Set(skw, fetched)
				continue

			# Nope. Failed.
			raise MissingArgumentError(f"Static key-word argument {skw} could not be Fetched.")

		this.arg.valid.static = True


	# Pull all propagating precursor methods into *this.
	# DO NOT USE Fetch() IN THIS METHOD!
	def PopulateMethods(this):

		# In order for this to work properly, each method needs to be a distinct object; hence the need for deepcopy.
		# In the future, we might be able to find a way to share code objects between Functors. However, for now we will allow each Functor to modify its classmethods as it pleases.

		# We have to use util.___Attr() because some sources might have '.'s in them.

		for source, honorPropagate in this.method.sources.items():
			if (not util.HasAttr(this, source)):
				logging.debug(f"Could not find {source}; will not pull in its methods.")
				continue

			methodSource = util.GetAttr(this, source)
			if (not isinstance(methodSource, dict)):
				logging.debug(f"{source} is not a dict; will not pull in its methods.")
				continue

			logging.debug(f"Populating methods from {source}.")
			for method in methodSource.values():
				if (honorPropagate and not method.propagate):
					continue
				if (method.name in this.methods.keys() and honorPropagate):
					existingMethod = this.methods[method.name]
					if (not existingMethod.inheritMethods):
						continue

					methodToInsert = deepcopy(method)
					methodToInsert.epidef = this
					methodToInsert.UpdateSource()

					if (existingMethod.inheritedMethodsFirst):
						logging.debug(f"Will call {method.name} from {source} to prior to this.")
						methodToInsert.next.append(this.methods[method.name])
						this.methods[method.name] = methodToInsert
					else:
						logging.debug(f"Appending {method.name} from {source} to this.")
						this.methods[method.name].next.append(methodToInsert)
				else:
					this.methods[method.name] = deepcopy(method)
					this.methods[method.name].epidef = this
					this.methods[method.name].UpdateSource()

		for method in this.methods.values():
			logging.debug(f"Populating method {this.name}.{method.name}({', '.join([a for a in method.arg.kw.required] + [a+'='+str(v) for a,v in method.arg.kw.optional.items()])})")

			# Python < 3.11
			# setattr(this, method.name, method.__call__.__get__(this, this.__class__))

			# appears to work for all python versions >= 3.8
			# setattr(this, method.name, method.__call__.__get__(method, method.__class__))
			
			setattr(this, method.name, types.MethodType(method, this))


	# Set this.precursor
	# Also set this.executor because it's easy.
	def PopulatePrecursor(this):
		if (this.executor is None):
			if ('executor' in this.kwargs):
				this.executor = this.kwargs.pop('executor')
			else:
				this.executor = ExecutorTracker.GetLatest()
		if (not this.executor):
			logging.warning(f"{this.name} was not given an 'executor'. Some features will not be available.")

		if ('precursor' in this.kwargs and this.kwargs['precursor'] is not None):
			this.precursor = this.kwargs.pop('precursor')
			logging.debug(f"{this.name} was preceded by {this.precursor.name}")
		else:
			this.precursor = None
			logging.debug(f"{this.name} was preceded by None")


	# Override this with any additional argument validation you need.
	# This is called before BeforeFunction(), below.
	def ValidateArgs(this):
		# logging.debug(f"this.kwargs: {this.kwargs}")
		# logging.debug(f"required this.kwargs: {this.arg.kw.required}")

		if (this.feature.mapArgs):
			if (len(this.args) > len(this.arg.mapping)):
				raise MissingArgumentError(f"{this.name} called with too many arguments. Got ({len(this.args)}) {this.args} but expected at most ({len(this.arg.mapping)}) {this.arg.mapping}")
			argMap = dict(zip(this.arg.mapping[:len(this.args)], this.args))
			logging.debug(f"Setting values from args: {argMap}")
			for arg, value in argMap.items():
				this.Set(arg, value)

		#NOTE: In order for *this to be called multiple times, required and optional kwargs must always be fetched and not use stale data from *this.

		if (this.arg.kw.required):
			for rkw in this.arg.kw.required:
				if (this.feature.mapArgs):
					if (rkw in argMap.keys()):
						continue
				
				logging.debug(f"Fetching required value {rkw}...")
				fetched, found = this.FetchWithout(['this'], rkw, start = False)
				if (found):
					this.Set(rkw, fetched)
					continue

				# Nope. Failed.
				logging.error(f"{rkw} required but not found.")
				raise MissingArgumentError(f"Key-word argument {rkw} could not be Fetched.")

		if (this.arg.kw.optional):
			for okw, default in this.arg.kw.optional.items():
				if (this.feature.mapArgs):
					if (okw in argMap.keys()):
						continue

				this.Set(okw, this.FetchWithout(['this'], okw, default=default))

	# When Fetching what to do next, everything is valid EXCEPT the environment. Otherwise, we could do something like `export next='nop'` and never quit.
	# A similar situation arises when using the global config for each Functor. We only use the global config if *this has no precursor.
	def PopulateNext(this):
		dontFetchFrom = [
			'this',
			'environment',
			'executor',
			'globals'
		]
		# Let 'next' evaluate its expressions if it chooses to. We don't need to do that pre-emptively.
		this.Set('next', this.FetchWithout(dontFetchFrom, 'next', []), evaluateExpressions=False)


	# Make sure that precursors have provided all necessary methods for *this.
	# NOTE: these should not be static nor cached, as calling something else before *this will change the behavior of *this.
	def ValidateMethods(this):
		for method in this.method.required:
			if (util.HasAttr(this, method) and callable(util.GetAttr(this, method))):
				continue

			raise MissingMethodError(f"{this.name} has no method: {method}")


	# RETURNS whether or not we should trigger the next Functor.
	# Override this to add in whatever checks you need.
	def ValidateNext(this, next):
		return True


	# Hook for whatever logic you'd like to run before the next Functor is called.
	# FIXME: This isn't actually called.
	def PrepareNext(this, next):
		pass


	# Call the next Functor.
	# RETURN the result of the next Functor or None.
	def CallNext(this):
		# TODO: Why would next ever not be a list This should be the same as the FIXME below.s
		if (not this.next or not isinstance(this.next, list) or len(this.next) == 0):
			return None
		
		# Something odd happens here; we've been getting:
		# AttributeError("'builtin_function_or_method' object has no attribute 'pop'")
		# But that implies we're getting a valid next object that is not a list.
		# FIXME: Debug this.
		proceedToNext = False
		next = None
		nextName = ""
		try:
			next = this.next.pop(0)
			if (isinstance(next, str)):
				nextName = next
			else:
				nextName = next.name
			proceedToNext = True
		except Exception as e:
			logging.error(f"{this.name} not proceeding to next: {e}; next: {nextName} (from {this.next})")
			return None

		if (proceedToNext):
			if (not this.ValidateNext(next)):
				raise InvalidNext(f"Failed to validate {next}")

			if (this.GetExecutor()):
				return this.GetExecutor().Execute(next, precursor=this, next=this.next)
			
			return next(precursor=this, next=this.next)


	# Prepare *this for any kind of operation.
	# All initialization should be done here.
	# RETURN boolean indicating whether or not *this is ready to do work.
	def WarmUp(this, *args, **kwargs):
		if (FunctorTracker.Instance().sequence.current.running):
			# We just started a new sequence. We're not ready to do work yet.
			if (FunctorTracker.Instance().sequence.stage[FunctorTracker.Instance().sequence.current.stage].state == 'initiated'):
				this.incomplete = True
				this.abort.WarmUp = True
				FunctorTracker.Instance().sequence.stage[FunctorTracker.Instance().sequence.current.stage].state = 'ready'
		# NOTE: this.abortWarmUp will (should) be set by the precursor before calling *this.
		
		if (not this.incomplete):
			this.args = []
			this.kwargs = {}

		this.args += args
		this.kwargs.update(kwargs)

		if (this.abort.WarmUp):
			return False
			
		this.result.code = 0
		this.result.data = util.DotDict()
		
		try:
			this.PopulatePrecursor()
			if (this.executor):
				this.executor.BeginPlacing(this.name)
			this.Initialize() # nop on call 2+
			this.PopulateMethods() # Doesn't require Fetch; depends on precursor
			this.ParseInitialArgs() # Usually where config is read in.
			this.ValidateStaticArgs() # nop on call 2+
			this.PopulateNext()
			this.ValidateArgs()
			this.ValidateMethods()
			if (this.executor):
				this.executor.ResolvePlacementOf(this.name)

		except Exception as e:

			# Allow partial function calls
			if (isinstance(e, MissingArgumentError) and this.feature.autoReturn):
				this.incomplete = True
				return False
			
			if (this.feature.raiseExceptions):
				raise e
			else:
				logging.error(f"ERROR: {e}")
				util.LogStack()
		
		this.incomplete = False
		return True


	# Make functor.
	# Don't worry about this; logic is abstracted to Function
	def __call__(this, *args, **kwargs) :
		args_repr = [repr(arg) for arg in args]
		kwargs_repr = {k: repr(v) for k, v in kwargs.items()}  
		logging.info(f"{this.name} ({args_repr}, {kwargs_repr}) {{")
		FunctorTracker.Push(this)

		ret = None
		nextRet = None

		try:
			this.WarmUp(*args, **kwargs)

			# TODO: Can we make this more performant? We should avoid doing this every time if we can.
			isSequence = this.WillPerformSequence()
			if (isSequence):
				FunctorTracker.InitiateSequence() # Has to be after WarmUp.

			if (this.incomplete):
				logging.debug(f"{this.name} incomplete.")
				logging.info(f"return {ret}")
				FunctorTracker.Pop(this)
				logging.info(f"}} ({this.name})")
				return this
			
			logging.debug(f"{this.name}({this.args}, {this.kwargs})")

			getattr(this, f"Before{this.method.function}")()
			ret = getattr(this, this.method.function)()

			if (getattr(this, f"Did{this.method.function}Succeed")()):
					this.result.code = 0
					# logging.info(f"{this.name} successful!")
					nextRet = this.CallNext()
			elif (this.feature.rollback):
				logging.warning(f"{this.name} failed. Attempting Rollback...")
				ret = getattr(this, this.method.rollback)()
				if (getattr(this, f"Did{this.method.rollback}Succeed")()):
					this.result.code = 1
					# logging.info(f"Rollback succeeded. All is well.")
					nextRet = this.CallNext()
				else:
					this.result.code = 2
					logging.error(f"ROLLBACK FAILED! SYSTEM STATE UNKNOWN!!!")
			else:
				this.result.code = 3
				logging.error(f"{this.name} failed.")

			getattr(this, f"After{this.method.function}")()

		except Exception as e:
			if (this.feature.raiseExceptions):
				raise e
			else:
				logging.error(f"ERROR: {e}")
				util.LogStack()

		if (this.feature.raiseExceptions and this.result.code > 1):
			raise FunctorError(f"{this.name} failed with result {this.result.code}: {this.result}")

		if (nextRet is not None):
			ret = nextRet
		elif (this.feature.autoReturn):
			if (this.result.data is None):
				this.result.data = ret
			elif (not 'returned' in this.result.data):
					this.result.data.returned = ret
			else:
				pass

			ret = this

		logging.info(f"return {ret} ({[type(r) for r in ret] if type(ret) in [tuple, list] else type(ret)})")
		FunctorTracker.Pop(this)
		logging.info(f"}} ({this.name})")

		return ret


	# Reduce the work required to access return values.
	# Make it possible to access related classes on the fly.
	#TODO: enable access of non existent members via the recovery machinery (e.g. this.retrievedViaTheNetwork.whatever)
	def __getattr__(this, attribute):
		try:
			this.__getattribute__(attribute)
		except:
			try:
				return this.__dict__[attribute]
			except:
				try:
					return BackwardsCompatible.Get(this, attribute)
				except:
					try:
						# Easy access to return values.
						return this.result.data[attribute]
					except:
						raise AttributeError(f"{this.name} has no attribute {attribute}")


	# Adapter for @recoverable.
	# See Recoverable.py for details
	def GetExecutor(this):
		return this.executor


	# Add support for deepcopy.
	# Copies everything besides methods; those will be created by PopulateMethods or removed.
	def __deepcopy__(this, memodict=None):
		logging.debug(f"Creating new {this.__class__} from {this.name}")
		cls = this.__class__
		ret = cls.__new__(cls)
		ret.__init__()

		memodict[id(this)] = ret

		# Huh?
		try:
			for key, val in [tup for tup in this.__dict__.items() if tup[0] not in ['methods']]:
				try:
					if (callable(val)):
						# PopulateMethods will take care of recreating skipped Methods
						# All other methods are dropped since they apparently have problems on some implementations.
						continue
					if (key in this.cloning.exclusions):
						continue
					setattr(ret, key, deepcopy(val, memodict))
				except:
					pass
		except:
			for key, val in [tup for tup in this.__dict__().items() if tup[0] not in ['methods']]:
				try:
					if (callable(val)):
						# PopulateMethods will take care of recreating skipped Methods
						# All other methods are dropped since they apparently have problems on some implementations.
						continue
					if (key in this.cloning.exclusions):
						continue
					setattr(ret, key, deepcopy(val, memodict))
				except:
					pass
		return ret
	

	# Enable sequences to be built/like/this
	def __truediv__(this, next):
		if (not isinstance(next, Functor)):
			return this
		this.next.append(next)
		next.abort.WarmUp = False
		return this.CallNext()


	# Avert your eyes!
	# This is deep black magick fuckery.
	# And no. There does not appear to be any other way to do this on CPython <=3.11
	def WillPerformSequence(this, backtrack=2):
		try:
			# NOTE: 11 is apparently the code for the __truediv__ division operator (/). On this system. For now...
			return [i for i in [i for i in dis.get_instructions(eval(f"inspect.currentframe(){'.f_back' * backtrack}.f_code")) if i.opname == 'BINARY_OP'] if i.arg == 11] > 0
		except:
			# Yeah...
			return False


	######## START: Fetch Locations ########

	def fetch_location_this(this, varName, default, fetchFrom, attempted):
		if (util.HasAttr(this, varName)):
			return util.GetAttr(this, varName), True
		return default, False

	def fetch_location_args(this, varName, default, fetchFrom, attempted):

		# this.args can't be searched.

		for key, val in this.kwargs.items():
			if (key == varName):
				return val, True
		return default, False


	def fetch_location_epidef(this, varName, default, fetchFrom, attempted):
		if (this.epidef is None):
			return default, False
		return this.epidef.FetchWithAndWithout(['this'], ['environment', 'globals', 'executor'], varName, default, fetchFrom, False, attempted)


	def fetch_location_caller(this, varName, default, fetchFrom, attempted):
		if (this.caller is None):
			return default, False
		return this.caller.FetchWithAndWithout(['this'], ['environment', 'globals', 'executor'], varName, default, fetchFrom, False, attempted)


	def fetch_location_precursor(this, varName, default, fetchFrom, attempted):
		if (this.precursor is None):
			return default, False
		return this.precursor.FetchWithAndWithout(['this'], ['environment', 'globals', 'executor'], varName, default, fetchFrom, False, attempted)



	# Call the Executor's Fetch method.
	# Exclude 'environment' because we can check that ourselves.
	def fetch_location_executor(this, varName, default, fetchFrom, attempted):
		if (not this.GetExecutor()):
			return default, False
		return this.GetExecutor().FetchWithout(['environment'], varName, default, fetchFrom, False, attempted)


	#NOTE: There is no config in the default Functor. This is done for the convenience of children.
	def fetch_location_config(this, varName, default, fetchFrom, attempted):
		if (not util.HasAttr(this, 'config') or this.config is None):
			return default, False

		for key, val in dict(this.config).items():
			if (key == varName):
				return val, True

		return default, False


	def fetch_location_globals(this, varName, default, fetchFrom, attempted):
		if (util.HasAttr(builtins, varName)):
			return util.GetAttr(builtins, varName), True
		return default, False


	def fetch_location_environment(this, varName, default, fetchFrom, attempted):
		envVar = os.getenv(varName)
		if (envVar is not None):
			return envVar, True
		envVar = os.getenv(varName.upper())
		if (envVar is not None):
			return envVar, True
		return default, False

	######## END: Fetch Locations ########


def METHOD_PENDING_POPULATION(obj, *args, **kwargs):
	raise MethodPendingPopulation("METHOD PENDING POPULATION")

# Store the new method in the class
def PrepareClassMethod(cls, name, methodToAdd):
	# There is a potential bug here: if the class derives from a class which already has the classMethods static member, this will add to the PARENT class's classMethods. Thus, 2 classes with different methods will share those methods via their shared parent.
	if (not hasattr(cls, 'classMethods') or not isinstance(cls.classMethods, dict)):
		cls.classMethods = {}
	else:
		# to account for the bug above, shadow classMethods out of the base class & into the derived.
		setattr(cls, 'classMethods', getattr(cls, 'classMethods').copy())

	cls.classMethods[name] = methodToAdd

	# Self-destruct by replacing the decorated function.
	# We rely on Functor.PopulateMethods to re-establish the method as callable.
	# It seems like this just outright removes the methods. There may be an issue with using __get__ this way.
	# Regardless deleting the method is okay as long as we add it back before anyone notices.
	setattr(cls, name, METHOD_PENDING_POPULATION.__get__(cls))

# Use the @method() decorator to turn any class function into an eons Method Functor.
# Methods are Functors which can be implicitly transferred between classes (see Functor.PopulateMethods)
# Using Methods also gives us full control over the execution of your code; meaning, we can change how Python interprets what you wrote!
# All Methods will be stored in the method member of your Functor. However, you shouldn't need to access that.
#
# If you would like to specify a custom implementation, set the 'impl' kwarg (e.g. @method(impl='MyMethodImplementation'))
# Beside 'impl', all key-word arguments provided to the @method() decorator will be set as member variables of the created Method.
# For example, to set whether or not the Method should be propagated, you can use @method(propagate=True).
# This means, you can create a custom means of interpreting your code with your own feature set and still use this @method decorator.
# Perhaps you'd like something along the lines of: @method(impl='MakeAwesome', awesomeness=10000).
# NOTE: in order for impl to work, the implementation class must already be Registered (or this must be called from an appropriate @recoverable function).
def method(impl='Method', **kwargs):

	# Class decorator with __set_name__, as described here: https://stackoverflow.com/questions/2366713/can-a-decorator-of-an-instance-method-access-the-class
	class MethodDecorator:
		def __init__(this, function):
			this.function = function

		# Apparently, this is called when the decorated function is constructed.
		def __set_name__(this, cls, functionName):
			logging.debug(f"Constructing new method for {this.function} in {cls}")

			# Create and configure a new Method

			methodToAdd = SelfRegistering(impl)
			methodToAdd.Constructor(this.function, cls)
			for key, value in kwargs.items():
				setattr(methodToAdd, key, value)

			PrepareClassMethod(cls, functionName, methodToAdd)

	return MethodDecorator

class Method(Functor):

	def __init__(this, name=INVALID_NAME()):
		super().__init__(name)

		# Methods do not fetch from the environment by default.
		this.fetch.use.remove('environment')

		# Whether or not *this should be combined with other Methods of the same name.
		this.inheritMethods = True

		# Where should inherited methods be inserted?
		# First here means "before *this".
		# If False, inherited code will be run after *this.
		this.inheritedMethodsFirst = True # otherwise ...Last

		# Propagation allows for Functors called after that which defines *this to also call *this.
		# This system allows for partial, implicit inheritance.
		# By default, Methods will not be propagated. Use @propagate to enable propagation.
		this.propagate = False

		# We don't care about these checks right now.
		# Plus, we can't exactly wrap 2 functions even if we wanted to Rollback.
		this.functionSucceeded = True
		this.rollbackSucceeded = True
		this.feature.rollback = False

		# Methods,by default, do not return themselves.
		this.feature.autoReturn = False

		# The source code of the function we're implementing.
		this.source = ""

		this.original = util.DotDict()
		this.original.cls = util.DotDict()
		this.original.cls.object = None
		this.original.cls.name = 'None'
		this.original.function = None

		this.arg.mapping = ['epidef']


	# Make *this execute the code in this.source
	def UpdateSource(this):
		wrappedFunctionName = f'_eons_method_{this.name}'
		completeSource = f'''\
def {wrappedFunctionName}(this):
{this.source}
'''
		if (this.executor and this.executor.verbosity > 3):
			logging.debug(f"Source for {this.name} is:\n{completeSource}")
		code = compile(completeSource, '', 'exec')
		exec(code)
		exec(f'this.Function = {wrappedFunctionName}.__get__(this, this.__class__)')


	# Parse arguments and update the source code
	# TODO: Implement full python parser to avoid bad string replacement (e.g. "def func(self):... self.selfImprovement" => "... this.epidef.this.epidef.Improvement").
	def PopulateFrom(this, function):
		this.source = ':'.join(inspect.getsource(function).split(':')[1:]) #Remove the first function definition

		args = inspect.signature(function, follow_wrapped=False).parameters
		thisSymbol = next(iter(args))
		#del args[thisSymbol] # ??? 'mappingproxy' object does not support item deletion
		this.source = this.source.replace(thisSymbol, 'this.epidef')

		first = True
		for arg in args.values(): #args.values[1:] also doesn't work.
			if (first):
				first = False
				continue

			replaceWith = arg.name

			if (arg.kind == inspect.Parameter.VAR_POSITIONAL):
				replaceWith = 'this.args'

			elif (arg.kind == inspect.Parameter.VAR_KEYWORD):
				replaceWith = 'this.kwargs'

			else:
				if (arg.default != inspect.Parameter.empty):
					this.arg.kw.optional[arg.name] = arg.default
				else:
					this.arg.kw.required.append(arg.name)
				replaceWith = f'this.{arg.name}'

				if (arg.kind in [inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY]):
					this.arg.mapping.append(arg.name)

			this.source = this.source.replace(arg.name, replaceWith)


	# When properly constructing a Method, rely only on the function *this should implement.
	# The class and all other properties are irrelevant. However, they are provided and intended for debugging only.
	def Constructor(this, function, cls):
		this.name = function.__name__
		this.original.cls.object = cls
		if (this.original.cls.object):
			this.original.cls.name = this.original.cls.object.__name__
		this.original.function = function

		this.PopulateFrom(function)
		
		# UpdateSource is called by Functor.PopulateMethods()
		# this.UpdateSource()


	# Grab any known and necessary args from this.kwargs before any Fetch calls are made.
	def PopulatePrecursor(this):
		if (not this.epidef):
			raise MissingArgumentError(f"Call {this.name} from a class instance: {this.original.cls.name}.{this.name}(...). Maybe Functor.PopulateMethods() hasn't been called yet?")

		this.executor = this.epidef.executor

		if ('precursor' in this.kwargs):
			this.precursor = this.kwargs.pop('precursor')
		else:
			this.precursor = None


	# Next is set by Functor.PopulateMethods.
	# We  definitely don't want to Fetch 'next'.
	def PopulateNext(this):
		pass


	# Method.next should be a list of other Methods, as opposed to the standard string; so, instead of Executor.Execute..., we can directly invoke whatever is next.
	# We skip all validation here.
	# We also don't pass any args that were given in the initial function call. Those can all be Fetched from 'precursor'.
	def CallNext(this):
		if (not this.next):
			return None

		for next in this.next:
			next(precursor=this)


# The standard Functor extends Functor to add a set of standard members and methods.
# This is similar to the standard library in C and C++
# You must inherit from *this if you would like to use the functionality *this provides. The methods defined will not be propagated.
class StandardFunctor(Functor):
	def __init__(this, name="Standard Functor"):
		super().__init__(name)

	# Override this and do whatever!
	# This is purposefully vague.
	def Function(this):
		pass


	# Undo any changes made by UserFunction.
	# Please override this too!
	def Rollback(this):
		pass


	# Override this to check results of operation and report on status.
	# Override this to perform whatever success checks are necessary.
	def DidFunctionSucceed(this):
		return this.functionSucceeded


	# RETURN whether or not the Rollback was successful.
	# Override this to perform whatever success checks are necessary.
	def DidRollbackSucceed(this):
		return this.rollbackSucceeded


	######## START: UTILITIES ########

	# RETURNS: an opened file object for writing.
	# Creates the path if it does not exist.
	@method()
	def CreateFile(this, file, mode="w+"):
		Path(os.path.dirname(os.path.abspath(file))).mkdir(parents=True, exist_ok=True)
		return open(file, mode)

	# Copy a file or folder from source to destination.
	# This really shouldn't be so hard...
	# root allows us to interpret '/' as something other than the top of the filesystem.
	@method()
	def Copy(this, source, destination, root='/'):
		if (source.startswith('/')):
			source = str(Path(root).joinpath(source[1:]).resolve())
		else:
			source = str(Path(source).resolve())
		
		destination = str(Path(destination).resolve())
		
		Path(destination).parent.mkdir(parents=True, exist_ok=True)

		if (os.path.isfile(source)):
			logging.debug(f"Copying file {source} to {destination}")
			try:
				shutil.copy(source, destination)
			except shutil.Error as exc:
				errors = exc.args[0]
				for error in errors:
					src, dst, msg = error
					logging.debug(f"{msg}")
		elif (os.path.isdir(source)):
			logging.debug(f"Copying directory {source} to {destination}")
			try:
				shutil.copytree(source, destination)
			except shutil.Error as exc:
				errors = exc.args[0]
				for error in errors:
					src, dst, msg = error
					logging.debug(f"{msg}")
		else:
			logging.error(f"Could not find source to copy: {source}")

	# Delete a file or folder
	@method()
	def Delete(this, target):
		if (not os.path.exists(target)):
			logging.debug(f"Unable to delete nonexistent target: {target}")
			return
		if (os.path.isfile(target)):
			logging.debug(f"Deleting file {target}")
			os.remove(target)
		elif (os.path.isdir(target)):
			logging.debug(f"Deleting directory {target}")
			try:
				shutil.rmtree(target)
			except shutil.Error as exc:
				errors = exc.args[0]
				for error in errors:
					src, dst, msg = error
					logging.debug(f"{msg}")

	# Run whatever.
	# DANGEROUS!!!!!
	# RETURN: Return value and, optionally, the output as a list of lines.
	@method()
	def RunCommand(this, command, saveout=False, raiseExceptions=True):
		logging.debug(f"================ Running command: {command} ================")
		process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
		output = []
		while process.poll() is None:
			line = process.stdout.readline().decode('utf8')[:-1]
			if (saveout):
				output.append(line)
			if (line):
				logging.debug(f"| {line}")  # [:-1] to strip excessive new lines.

		message = f"Command returned {process.returncode}: {command}"
		logging.debug(message)
		if (raiseExceptions and process.returncode is not None and process.returncode):
			raise CommandUnsuccessful(message)
		
		logging.debug(f"================ Completed command: {command} ================")
		if (saveout):
			return process.returncode, output
		
		return process.returncode
	######## END: UTILITIES ########


# Use an ErrorStringParser for each "parsers" in order to avoid having to override the GetSubjectFromError method and create a new class for every error you want to handle.
# ErrorStringParsers enable ErrorResolutions to be created on a per-functionality, rather than per-error basis, reducing the total amount of duplicate code.
# Each error has a different string. In order to get the object of the error, we have to know where the object starts and ends.
# NOTE: this assumes only 1 object per string. Maybe fancier parsing logic can be added in the future.
#
# startPosition is always positive
# endPosition is always negative
class ErrorStringParser:

	def __init__(this, applicableError, startPosition, endPosition):
		this.applicableError = applicableError
		this.startPosition = startPosition
		this.endPosition = endPosition

	def Parse(this, errorString):
		end = this.endPosition
		if (not end):
			end = len(errorString)
		return errorString[this.startPosition:end]


# ErrorResolution is a Functor which can be executed when an Exception is raised.
# The goal of this class is to do some kind of work that will fix the problem on the second try of whatever generated the error.
class ErrorResolution(StandardFunctor):

	def __init__(this, name=INVALID_NAME()):
		super().__init__(name)

		# What errors, as ErrorStringParser objects, is *this prepared to handle?
		this.parsers = []

		this.error = util.DotDict()
		this.error.object = None
		this.error.type = ""
		this.error.string = ""
		this.error.subject = ""
		this.error.resolution = util.DotDict()
		this.error.resolution.successful = False
		this.error.resolution.stack = {}

		# Provided directly from the recoverable decorator.
		this.arg.kw.optional["obj"] = None
		this.arg.kw.optional["function"] = None

		# We do want to know whether or not we should attempt to run whatever failed again.
		# So, let's store that in functionSucceeded. Meaning if this.functionSucceeded, try the original method again.
		# No rollback, by default and definitely don't throw Exceptions.
		this.feature.rollback = False
		this.feature.raiseExceptions = False
		this.feature.autoReturn = False
		this.functionSucceeded = True

		this.functionSucceeded = True

	# Put your logic here!
	def Resolve(this):
		# You get the following members:
		# this.error (an Exception)
		# this.error.string (a string cast of the Exception)
		# this.error.type (a string)
		# this.error.subject (a string or whatever you return from GetSubjectFromError())

		# You get the following guarantees:
		# *this has not been called on this particular error before.
		# the error given is applicable to *this per this.parsers

		###############################################
		# Please throw errors if something goes wrong #
		# Otherwise, set this.error.resolution.successful   #
		###############################################
		
		pass



	# Helper method for creating ErrorStringParsers
	# To use this, simply take an example output and replace the object you want to extract with "SUBJECT"
	def ApplyTo(this, error, exampleString):
		match = re.search('SUBJECT', exampleString)
		this.parsers.append(ErrorStringParser(error, match.start(), match.end() - len(exampleString)))


	# Get the type of this.error as a string.
	def GetErrorType(this):
		return type(this.error.object).__name__


	# Get an actionable object from the error.
	# For example, if the error is 'ModuleNotFoundError', what is the module?
	def GetSubjectFromError(this):
		for parser in this.parsers:
			if (parser.applicableError != this.error.type):
				continue

			this.error.subject = parser.Parse(this.error.string)
			return

		raise ErrorResolutionError(f"{this.name} cannot parse error object from ({this.error.type}): {str(this.error.object)}.")


	# Determine if this resolution method is applicable.
	def CanProcess(this):
		return this.GetErrorType() in [parser.applicableError for parser in this.parsers]


	# Grab any known and necessary args from this.kwargs before any Fetch calls are made.
	def ParseInitialArgs(this):
		super().ParseInitialArgs()
		if ('error' in this.kwargs):
			this.error.object = this.kwargs.pop('error')
			# Just assume the error is an actual Exception object.
		else:
			raise ErrorResolutionError(f"{this.name} was not given an error to resolve.")

		this.error.string = str(this.error.object)
		this.error.type = this.GetErrorType()

		# Internal member to avoid processing duplicates
		this.error.resolution.stack = this.executor.error.resolution.stack


	# Error resolution is unchained.
	def PopulateNext(this):
		this.next = []


	# Override of Functor method.
	# We'll keep calling this until an error is raised.
	def Function(this):
		this.functionSucceeded = True
		this.error.resolution.successful = True
		
		if (not this.CanProcess()):
			this.error.resolution.successful = False
			return this.error.resolution.stack, this.error.resolution.successful

		if (not this.error.string in this.error.resolution.stack.keys()):
			this.error.resolution.stack.update({this.error.string:[]})
		
		if (this.name in this.error.resolution.stack[this.error.string]):
			raise FailedErrorResolution(f"{this.name} already tried and failed to resolve {this.error.type}: {this.error.string}.")

		this.GetSubjectFromError()

		try:
			this.Resolve()
		except Exception as e:
			logging.error(f"Error resolution with {this.name} failed: {e}")
			util.LogStack()
			this.functionSucceeded = False
		
		this.error.resolution.stack[this.error.string].append(this.name)
		return this.error.resolution.stack, this.error.resolution.successful


# Executor: a base class for user interfaces.
# An Executor is a functor and can be executed as such.
# For example
#	class MyExecutor(Executor):
#		def __init__(this):
#			super().__init__()
#	. . .
#	myprogram = MyExecutor()
#	myprogram()
# NOTE: Diamond inheritance of Datum.
class Executor(DataContainer, Functor):

	def __init__(this, name=INVALID_NAME(), description="Eons python framework. Extend as thou wilt."):
		this.SetupLogging()

		super().__init__(name)

		this.arg.kw.optional['log_time_stardate'] = True
		this.arg.kw.optional['log_indentation'] = True
		this.arg.kw.optional['log_tab_width'] = 2
		this.arg.kw.optional['log_aggregate'] = True
		this.arg.kw.optional['log_aggregate_url'] = "https://eons.sh/log"

		# Executors should have control over their returns, if they have any.
		this.feature.autoReturn = False

		# Error resolution settings
		this.error = util.DotDict()
		this.error.resolve = True
		this.error.depth = 0
		this.error.resolution = util.DotDict()
		this.error.resolution.stack = {}
		this.error.resolvers = [ # order matters: FIFO (first is first).
			'find_by_fetch',
			'import_module',
			'namespace_lookup',
			'install_from_repo_with_default_package_type',
			'install_from_repo',
			'install_with_pip'
		]

		# Caching is required for Functor's arg.kw.static and other static features to be effective.
		# This is used in Execute().
		this.cache.functors = {}

		# General system info
		this.cwd = os.getcwd()
		this.syspath = sys.path

		# CLI (or otherwise) args
		this.arg.parser = argparse.ArgumentParser(description = description)
		this.parsedArgs = None
		this.extraArgs = None
		
		# How much information should we output?
		this.verbosity = 0

		# config is loaded with the contents of a JSON config file specified by --config / -c or by the default.config.files location, below.
		this.config = None
		this.configType = None

		# *this will keep track of any global variables it creates.
		# All globals should be read only.
		# Dict is in the form of {variable_name: set_by_fetch}
		# See SetGlobal(), below.
		this.globals = {}

		# The globalContextKey is mainly used for big, nested configs.
		# It serves as a means of leaving the name of various global values intact while changing their values.
		# For example, a method of some Functor might check service.name, but we might have a service for mysql, redis, etc. In this situation, we can say SetGlobalContextKey('mysql') and the Functor will operate on the mysql.service.name. Then, when we're ready, we SetGlobalContextKey('redis') and call the same Functor again to operate on the redis.service.name.
		# Thus, the globalContextKey allow those using global variables to remain naive of where those values are coming from.
		this.globalContextKey = None

		# Logging settings.
		this.log = util.DotDict()
		
		# Where should we log to?
		# Set by Fetch('log_file')
		this.log.file = None

		# All repository configuration.
		this.repo = util.DotDict()

		# The observatory is a means of communicating with Constellatus.
		# While the repo may provide any arbitrary data in zip format, Stars located from Constellatus are specially handled.
		this.observatory = util.DotDict()

		# Placement helps to construct the correct load order of Functors as they are installed.
		this.placement = util.DotDict()
		this.placement.max = 255
		this.placement.session = util.DotDict()
		
		# Defaults.
		# You probably want to configure these in your own Executors.
		this.default = util.DotDict()

		# Default registration settings.
		this.default.register = util.DotDict()
		
		# What directories should load when booting up?
		this.default.register.directories = []

		# Default repo settings.
		# See PopulateRepoDetails for more info.
		this.default.repo = util.DotDict()
		this.default.repo.directory = os.path.abspath(os.path.join(os.getcwd(), "./eons/"))

		# Package retrieval settings.
		this.default.package = util.DotDict()
		this.default.package.type = ""

		# Configuration ingestion settings.
		this.default.config = util.DotDict()
		
		# What files should we look for when loading config?
		this.default.config.files = ['config']

		# Allow the config file to be in multiple formats.
		# These are in preference order (e.g. if you want to look for a .txt file before a .json, add it to the top of the list).
		# Precedence should prefer more structured and machine-generated configs over file formats easier for humans to work with.
		this.default.config.extensions = [
			"json",
			"yaml",
			"yml",
			"py",
		]

		# We can't Fetch from everywhere while we're getting things going. However, these should be safe,
		this.fetch.useDuringSetup = ['args', 'config', 'environment']

		this.MaintainCompatibilityFor(2.0, {
			'error.resolve': 'resolveErrors',
			'error.resolvers': 'resolveErrorsWith',
			'error.resolution.stack': 'errorResolutionStack',
			'error.resolution.depth': 'errorRecursionDepth',
			'cache.functors': 'cachedFunctors',
			'arg.parser': 'argparser',
			'log.file': 'log_file',
			'default.register.directories': 'registerDirectories',
			'default.repo.directory': 'defaultRepoDirectory',
			'default.package.type': 'defaultPackageType',
			'default.config.files': 'defaultConfigFile',
			'default.config.extensions': 'configFileExtensions',
		})

		this.Configure()
		this.RegisterIncludedClasses()
		this.AddArgs()
		this.ResetPlacementSession()


	def SupportBackwardsCompatibility(this):
		super().SupportBackwardsCompatibility()
		if (this.compatibility < 3):
			if (type(this.default.config.files) is not list):
				this.default.config.files = [this.default.config.files]


	# Destructors do not work reliably in python.
	# NOTE: you CANNOT delete *this without first Pop()ing it from the ExecutorTracker.
	# def __del__(this):
	# 	ExecutorTracker.Instance().Pop(this)


	# Adapter for @recoverable.
	# See Recoverable.py for details
	def GetExecutor(this):
		return this


	# this.error.resolution.stack are whatever we've tried to do to fix whatever our problem is.
	# This method resets our attempts to remove stale data.
	def ClearErrorResolutionStack(this, force=False):
		if (force):
			this.error.depth = 0

		if (this.error.depth):
			this.error.depth = this.error.depth - 1

		if (not this.error.depth):
			this.error.resolution.stack = {}


	# Configure class defaults.
	# Override this to customize your Executor.
	def Configure(this):
		this.fetch.use.remove('executor') # No no no no!
		this.fetch.use.remove('precursor') # Not applicable here.

		# Usually, Executors shunt work off to other Functors, so we leave these True unless a child needs to check its work.
		this.functionSucceeded = True
		this.rollbackSucceeded = True

		this.asyncSession = FuturesSession()

	# Add a place to search for SelfRegistering classes.
	# These should all be relative to the invoking working directory (i.e. whatever './' is at time of calling Executor())
	def RegisterDirectory(this, directory):
		this.default.register.directories.append(os.path.abspath(os.path.join(this.cwd,directory)))


	# Global logging config.
	# Override this method to disable or change.
	# This method will add a 'setupBy' member to the root logger in order to ensure no one else (e.g. another Executor) tries to reconfigure the logger while we're using it.
	# The 'setupBy' member will be removed from the root logger by TeardownLogging, which is called in AfterFunction().
	def SetupLogging(this):
		try:
			util.AddLoggingLevel('recovery', logging.ERROR+1)
		except:
			# Could already be setup.
			pass

		class CustomFormatter(logging.Formatter):

			preFormat = util.console.GetColorCode('white', 'dark') + '__TIME__ '
			levelName = '[%(levelname)8s] '
			indentation = util.console.GetColorCode('blue', 'dark', styles=['faint']) + '__INDENTATION__' + util.console.GetColorCode('white', 'dark', styles=['none'])
			message = '%(message)s '
			postFormat = util.console.GetColorCode('white', 'dark') + '(%(filename)s:%(lineno)s)' + util.console.resetStyle

			formats = {
				logging.DEBUG: preFormat + levelName + indentation + util.console.GetColorCode('cyan', 'dark') + message + postFormat,
				logging.INFO: preFormat + levelName + indentation + util.console.GetColorCode('white', 'light') + message + postFormat,
				logging.WARNING: preFormat + levelName + indentation + util.console.GetColorCode('yellow', 'light') + message + postFormat,
				logging.ERROR: preFormat + levelName + indentation + util.console.GetColorCode('red', 'dark') + message + postFormat,
				logging.RECOVERY: preFormat + levelName + indentation + util.console.GetColorCode('green', 'light') + message + postFormat,
				logging.CRITICAL: preFormat + levelName + indentation + util.console.GetColorCode('red', 'light', styles=['bold']) + message + postFormat
			}

			def format(this, record):
				log_fmt = this.formats.get(record.levelno)

				executor = None
				if (hasattr(logging.getLogger(), 'setupBy')):
					executor = getattr(logging.getLogger(), 'setupBy')

					# The executor won't have populated its arg.kw.optional until after this method is effected.
					# So we wait until the last optional arg is set to start using the executor.
					if (not hasattr(executor, 'log_aggregate_url')):
						executor = None

				if (executor):
					# Add indentation.
					if (executor.log_indentation and executor.log_tab_width):
						log_fmt = log_fmt.replace('__INDENTATION__', f"|{' ' * (executor.log_tab_width - 1)}" * (FunctorTracker.GetCount() - 1)) # -1 because we're already in a Functor.
					else:
						log_fmt = log_fmt.replace('__INDENTATION__', ' ')

					# Add time.
					if (executor.log_time_stardate):
						log_fmt = log_fmt.replace('__TIME__', f"{EOT.GetStardate()}")
					else:
						log_fmt = log_fmt.replace('__TIME__', "%(asctime)s")

					# Aggregate logs remotely.
					if (executor.log_aggregate 
						and executor.repo.username is not None 
						and executor.repo.password is not None
						and record.module != 'connectionpool' # Prevent recursion.
						):
						aggregateEndpoint = executor.log_aggregate_url
						log = {
							'level': record.levelname,
							'message': record.getMessage(), # TODO: Sanitize to prevent 400 errors.
							'source': executor.name,
							'timestamp': EOT.GetStardate()
						}
						try:
							executor.asyncSession.put(aggregateEndpoint, json=log, auth=(executor.repo.username, executor.repo.password))
						except Exception as e:
							pass
				else:
					log_fmt = log_fmt.replace('__INDENTATION__', ' ')
					log_fmt = log_fmt.replace('__TIME__', "%(asctime)s")

				formatter = logging.Formatter(log_fmt, datefmt = '%H:%M:%S')
				return formatter.format(record)

		# Skip setting up logging if it's already been done.
		if (hasattr(logging.getLogger(), 'setupBy')):
			return
 
		logging.getLogger().handlers.clear()
		stderrHandler = logging.StreamHandler()
		stderrHandler.setLevel(logging.CRITICAL)
		stderrHandler.setFormatter(CustomFormatter())
		logging.getLogger().addHandler(stderrHandler)
		setattr(logging.getLogger(), 'setupBy', this)


	# Global logging de-config.
	def TeardownLogging(this):
		if (not hasattr(logging.getLogger(), 'setupBy')):
			return
		if (not logging.getLogger().setupBy == this):
			return
		delattr(logging.getLogger(), 'setupBy')


	# Logging to stderr is easy, since it will always happen.
	# However, we also want the user to be able to log to a file, possibly set in the config.json, which requires a Fetch().
	# Thus, setting up the log file handler has to occur later than the initial SetupLogging call.
	# Calling this multiple times will add multiple log handlers.
	def SetLogFile(this):
		this.Set('log_file', this.Fetch('log_file', None, this.fetch.useDuringSetup))
		if (this.log.file is None):
			return

		logFilePath = Path(this.log.file).resolve()
		if (not logFilePath.exists()):
			logFilePath.parent.mkdir(parents=True, exist_ok=True)
			logFilePath.touch()

		this.log.file = str(logFilePath) # because resolve() is nice.
		logging.info(f"Will log to {this.log.file}")

		logFormatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)')
		fileHandler = logging.FileHandler(this.log.file)
		fileHandler.setFormatter(logFormatter)
		fileHandler.setLevel(logging.DEBUG)
		logging.getLogger().addHandler(fileHandler)


	# Adds command line arguments.
	# Override this method to change. Optionally, call super().AddArgs() within your method to simply add to this list.
	def AddArgs(this):
		this.arg.parser.add_argument('--verbose', '-v', action='count', default=0)
		this.arg.parser.add_argument('--config', '-c', type=str, default=None, help='Path to configuration file containing only valid JSON.', dest='config')

		# We'll use Fetch instead
		# this.arg.parser.add_argument('--log', '-l', type=str, default=None, help='Path to log file.', dest='log')
		# this.arg.parser.add_argument('--no-repo', action='store_true', default=False, help='prevents searching online repositories', dest='no_repo')


	# End the current placement session (if any)
	def ResetPlacementSession(this):
		this.placement.session.active = False
		this.placement.session.level = this.placement.max
		this.placement.session.hierarchy = {}
		this.placement.session.current = []
		# logging.debug(f"Dependency placement session ended; level is now {this.placement.session.level}")

	# Track to the current location in the placement hierarchy.
	def GetPlacementSessionCurrentPosition(this):
		if (not this.placement.session.active):
			return None
		ret = this.placement.session.hierarchy
		for place in this.placement.session.hierarchy:
			ret = ret[place]
		return ret
	
	def BeginPlacing(this, toPlace):
		if (not this.placement.session.active):
			this.placement.session.active = True
		hierarchy = this.GetPlacementSessionCurrentPosition()
		hierarchy[toPlace] = {}
		this.placement.session.current.append(toPlace)
		this.placement.session.level -= 1
		logging.debug(f"Prepared to place dependencies for {toPlace}; level is now {this.placement.session.level}")

	# Once the proper location of a Functor has been derived, remove it from the hierarchy.
	# Additionally, if we're the last ones to play with the current session, reset it.
	def ResolvePlacementOf(this, placed):
		if (not this.placement.session.active):
			return
		try:
			this.placement.session.current.remove(placed)
			hierarchy = this.GetPlacementSessionCurrentPosition()
			if (not len(this.placement.session.current)):
				this.ResetPlacementSession()
			elif (hierarchy and placed in hierarchy.keys()):
				del hierarchy[placed]
				this.placement.session.level += 1
			logging.debug(f"Finished placing dependencies for {placed}; level is now {this.placement.session.level}")
		except:
			pass # key errors when getting an existing Functor...
		

	# Create any sub-class necessary for child-operations
	# Does not RETURN anything.
	def InitData(this):
		pass


	# Register included files early so that they can be used by the rest of the system.
	# If we don't do this, we risk hitting infinite loops because modular functionality relies on these modules.
	# NOTE: this method needs to be overridden in all children which ship included Functors, Data, etc. This is because __file__ is unique to the eons.py file, not the child's location.
	def RegisterIncludedClasses(this):
		includePaths = [
			'resolve',
			'method'
		]
		for path in includePaths:
			this.RegisterAllClassesInDirectory(str(Path(__file__).resolve().parent.joinpath(path)))


	# Executors should not have precursors
	def PopulatePrecursor(this):
		this.executor = this
		pass


	# Register all classes in each directory in this.default.register.directories
	def RegisterAllClasses(this):
		for d in this.default.register.directories:
			this.RegisterAllClassesInDirectory(os.path.join(os.getcwd(), d))
		this.RegisterAllClassesInDirectory(this.repo.registry)


	# Grok the configFile and return the results.
	@staticmethod
	def ParseConfigFile(executor, configType, configFile, functor=None):
		if (configType in ['py']):
			if (functor is None):
				raise ExecutorSetupError(f"Cannot parse python config file without a functor.")
			
			return functor(executor=executor).result.data
		elif (configType in ['json', 'yml', 'yaml']):
			# Yaml doesn't allow tabs. We do. Convert.
			return yaml.safe_load(configFile.read().replace('\t', '  '))
		else:
			raise ExecutorSetupError(f"Unknown configuration file type: {configType}")


	# Populate the configuration details for *this.
	def PopulateConfig(this):
		this.config = None
		this.configType = None

		if (this.parsedArgs.config is None):
			for file in this.default.config.files:
				for ext in this.default.config.extensions:
					possibleConfig = f"{file}.{ext}"
					if (Path(possibleConfig).exists()):
						this.parsedArgs.config = possibleConfig
						break

		logging.debug(f"Populating config from {this.parsedArgs.config}")

		if (this.parsedArgs.config is None):
			return

		if (not os.path.isfile(this.parsedArgs.config)):
			logging.error(f"Could not open configuration file: {this.parsedArgs.config}")
			return
		
		this.configType = this.parsedArgs.config.split('.')[-1]
		configFunctor = None
		if (this.configType in ['py']):
			this.RegisterAllClassesInDirectory(Path('./').joinpath('/'.join(this.parsedArgs.config.split('/')[:-1])))
			configFunctor = SelfRegistering(this.parsedArgs.config.split('/')[-1].split('.')[0])

		configFile = open(this.parsedArgs.config, "r")
		this.config = this.ParseConfigFile(this, this.configType, configFile, configFunctor)
		configFile.close()


	#  Get information for how to download packages.
	def PopulateRepoDetails(this):
		details = {
			"online": not this.Fetch('no_repo', False, ['this', 'args', 'config']),
			"store": this.default.repo.directory,
			"registry": str(Path(this.default.repo.directory).joinpath('registry').resolve()),
			"url": "https://api.infrastructure.tech/v1/package",
			"username": None,
			"password": None
		}
		for key, default in details.items():
			this.repo[key] = this.Fetch(f"repo_{key}", default=default)
	

	# Get information for interacting with Constellatus
	def PopulateObservatoryDetails(this):
		details = {
			"online": True,
			"url": "https://api.constellatus.com",
			"username": None,
			"password": None
		}
		for key, default in details.items():
			this.observatory[key] = this.Fetch(f"observatory_{key}", default=default)

	# How do we get the verbosity level and what do we do with it?
	# This method should set log levels, etc.
	def SetVerbosity(this, fetch=True):
		if (fetch):
			# Take the highest of -v vs --verbosity
			verbosity = this.EvaluateToType(this.Fetch('verbosity', 0, this.fetch.useDuringSetup))
			if (verbosity > this.verbosity):
				logging.debug(f"Setting verbosity to {verbosity}") # debug statements will be available when using external systems, like pytest.
				this.verbosity = verbosity

		if (this.verbosity == 0):
			logging.getLogger().handlers[0].setLevel(logging.CRITICAL)
			logging.getLogger().setLevel(logging.CRITICAL)
		if (this.verbosity == 1):
			logging.getLogger().handlers[0].setLevel(logging.WARNING)
			logging.getLogger().setLevel(logging.WARNING)
		elif (this.verbosity == 2):
			logging.getLogger().handlers[0].setLevel(logging.INFO)
			logging.getLogger().setLevel(logging.INFO)
		elif (this.verbosity >= 3):
			logging.getLogger().handlers[0].setLevel(logging.DEBUG)
			logging.getLogger().setLevel(logging.DEBUG)
			logging.getLogger('urllib3').setLevel(logging.WARNING)
		
		if (this.verbosity >= 5):
			logging.getLogger('urllib3').setLevel(logging.DEBUG)


	# Do the argparse thing.
	# Extra arguments are converted from --this-format to this_format, without preceding dashes. For example, --repo-url ... becomes repo_url ...
	# NOTE: YOU CANNOT USE @recoverable METHODS HERE!
	def ParseArgs(this):
		# Compatibility is a lie, this doesn't work.
		# compatibleArgParser = argparse.ArgumentParser(parents=[this.arg.parser, this.argparser])
		this.parsedArgs, extraArgs = this.arg.parser.parse_known_args()

		this.verbosity = this.parsedArgs.verbose

		# If verbosity was specified on the command line, let's print more info while reading in the config, etc.
		this.SetVerbosity(False)

		extraArgsKeys = []
		for index in range(0, len(extraArgs), 2):
			keyStr = extraArgs[index]
			keyStr = keyStr.replace('--', '').replace('-', '_')
			extraArgsKeys.append(keyStr)

		extraArgsValues = []
		for index in range(1, len(extraArgs), 2):
			extraArgsValues.append(extraArgs[index])

		this.extraArgs = dict(zip(extraArgsKeys, extraArgsValues))


	# Functor method.
	# We have to ParseArgs() here in order for other Executors to use ____KWArgs...
	def ParseInitialArgs(this):
		this.ParseArgs() # first, to enable debug and other such settings.

		# Track *this globally
		# This needs to be done before the config is populated, in case we use a py file that has External Methods.
		ExecutorTracker.Instance().Push(this)

		this.PopulateConfig()
		this.SetVerbosity()
		this.SetLogFile()
		logging.debug(f"<---- {this.name} (log level: {logging.getLogger().level}) ---->")
		logging.debug(f"Got extra arguments: {this.extraArgs}") # has to be after verbosity setting
		logging.debug(f"Got config contents: {this.config}")
		this.PopulateRepoDetails()
		this.PopulateObservatoryDetails()
		this.placement.max = this.Fetch('placement_max', 255, this.fetch.useDuringSetup)


	# Functor required method
	# Override this with your own workflow.
	def Function(this):
		
		# NOTE: class registration may instantiate other Executors.
		this.RegisterAllClasses()
		
		this.InitData()


	# By default, Executors do not act on this.next; instead, they make it available to all Executed Functors.
	def CallNext(this):
		pass


	# Close out anything we left open.
	def AfterFunction(this):
		this.TeardownLogging()


	def WarmUpFlow(this, flow):
		flow.WarmUp(executor=this)


	# Flows are domain-like strings which can be resolved to a Functor.
	@recoverable
	def Flow(this, flow):
		logging.debug(f"Calculating flow: {flow}")

		flowList = flow.split('.')
		flowList.reverse()
		current = this.GetRegistered(flowList.pop(0), 'flow')
		while (True):
			this.WarmUpFlow(current)
			if (not len(flowList)):
				break

			current = current.methods[flowList.pop(0)]
		return current()
	

	# Execute a Functor based on name alone (not object).
	# If the given Functor has been Executed before, the cached Functor will be called again. Otherwise, a new Functor will be constructed.
	@recoverable
	def Execute(this, functor, *args, **kwargs):
		if (isinstance(functor, str)):
			functorName = functor
			packageType = this.default.package.type
			if ('packageType' in kwargs):
				packageType = kwargs.pop('packageType')

			if (functorName in this.cache.functors):
				functor = this.cache.functors[functorName]
			else:
				functor = this.GetRegistered(functorName, packageType)
		else:
			functorName = functor.name

		logging.debug(f"Executing {functorName}({', '.join([str(a) for a in args] + [k+'='+str(v) for k,v in kwargs.items()])})")
		this.cache.functors.update({functorName: functor})
		return functor(*args, **kwargs, executor=this)


	# Attempts to download the given package from the repo url specified in calling args.
	# Will refresh registered classes upon success
	# RETURNS whether or not the package was downloaded. Will raise Exceptions on errors.
	# Does not guarantee new classes are made available; errors need to be handled by the caller.
	@recoverable
	def DownloadPackage(this,
		packageName,
		registerClasses=True,
		createSubDirectory=False):

		if (not this.repo.online):
			logging.debug(f"Refusing to download {packageName}; we were told not to use a repository.")
			return False

		logging.debug(f"Trying to download {packageName} from repository ({this.repo.url})")

		for path in ['store', 'registry']:
			if (Path(this.repo[path]).is_dir()):
				continue
			logging.debug(f"Creating directory {this.repo[path]}")
			Path(this.repo[path]).mkdir(parents=True, exist_ok=True)

		packageZipPath = os.path.join(this.repo.store, f"{packageName}.zip")

		url = f"{this.repo.url}/download?package_name={packageName}"

		auth = None
		if this.repo.username and this.repo.password:
			auth = requests.auth.HTTPBasicAuth(this.repo.username, this.repo.password)

		headers = {
			"Connection": "keep-alive",
		}

		packageQuery = requests.get(url, auth=auth, headers=headers, stream=True)

		if (packageQuery.status_code != 200):
			raise PackageError(f"Unable to download {packageName}")
		# let caller decide what to do next.

		packageSize = int(packageQuery.headers.get('content-length', 0))
		chunkSize = 1024 # 1 Kibibyte

		logging.debug(f"Writing {packageZipPath} ({packageSize} bytes)")
		packageZipContents = open(packageZipPath, 'wb+')

		progressBar = None
		if (this.verbosity >= 2):
			progressBar = tqdm(total=packageSize, unit='iB', unit_scale=True)

		for chunk in packageQuery.iter_content(chunkSize):
			packageZipContents.write(chunk)
			if (this.verbosity >= 2):
				progressBar.update(len(chunk))

		if (this.verbosity >= 2):
			progressBar.close()

		if (packageSize and this.verbosity >= 2 and progressBar.n != packageSize):
			raise PackageError(f"Package wrote {progressBar.n} / {packageSize} bytes")

		packageZipContents.close()

		if (not os.path.exists(packageZipPath)):
			raise PackageError(f"Failed to create {packageZipPath}")

		openArchive = ZipFile(packageZipPath, 'r')
		extractLoc = this.repo.store
		if (registerClasses):
			extractLoc = this.repo.registry
		if (createSubDirectory):
			extractLoc = os.path.join(extractLoc, packageName)
		elif (this.placement.session.active):
			extractLoc = os.path.join(extractLoc, str(this.placement.session.level))
		logging.debug(f"Extracting {packageZipPath} to {extractLoc}")
		openArchive.extractall(f"{extractLoc}")
		openArchive.close()
		os.remove(packageZipPath)

		if (registerClasses):
			this.RegisterAllClassesInDirectory(this.repo.registry)

		return True

	# Use Constellatus to grab a SelfRegistering class.
	def LocateStarCluster(this, starCluster):
		if (not this.observatory.online):
			logging.debug(f"Refusing to locate {starCluster}; we were told not to use an observatory.")
			raise ConstellatusError(f"Unable to locate {starCluster}: Observatory is offline.")
		
		logging.debug(f"Locating {starCluster}")

		url = f"{this.observatory.url}/{starCluster}"

		auth = None
		if this.observatory.username and this.observatory.password:
			auth = requests.auth.HTTPBasicAuth(this.observatory.username, this.observatory.password)

		headers = {
			"Connection": "keep-alive",
		}

		observation = requests.get(url, auth=auth, headers=headers, stream=True)

		if (observation.status_code != 200):
			raise ConstellatusError(f"Unable to locate {starCluster}")
		
		try:
			# Load the code from Constellatus into a module on the fly
			moduleName = starCluster.replace(':', '_').replace('.', '_')
			spec = importlib.util.spec_from_loader(moduleName, loader=None)
			module = importlib.util.module_from_spec(spec)
			exec(observation.content, module.__dict__)
			sys.modules[moduleName] = module
			globals()[moduleName] = module
			logging.debug(f"Completed observation of {starCluster}")
		except Exception as e:
			raise ConstellatusError(f"Unable to locate {starCluster}: {e}")


	# RETURNS and instance of a Datum, Functor, etc. (aka modules) which has been discovered by a prior call of RegisterAllClassesInDirectory()
	# Will attempt to register existing modules if one of the given name is not found. Failing that, the given package will be downloaded if it can be found online.
	# Both python modules and other eons modules of the same packageType will be installed automatically in order to meet all required dependencies of the given module.
	@recoverable
	def GetRegistered(this,
		registeredName,
		packageType="",
		namespace=None):

		if (packageType):
			packageType = "." + packageType
		
		namespacedRegisteredName = registeredName
		if (namespace):
			namespacedRegisteredName = Namespace(namespace).ToName() + registeredName

		try:
			registered = SelfRegistering(namespacedRegisteredName)
		except Exception as e:
			try:
				# If the Observatory is online, let's try to use Constellatus.
				this.LocateStarCluster(f"{str(Namespace(namespace))}{registeredName}{packageType}")
				registered = SelfRegistering(registeredName)
			except: # We don't care about Constellatus errors right now.

				# We couldn't get what was asked for. Let's try asking for help from the error resolution machinery.
				packageName = namespacedRegisteredName + packageType
				logging.error(f"While trying to instantiate {packageName}, got: {e}")
				raise HelpWantedWithRegistering(f"Trying to get SelfRegistering {packageName}")

		# NOTE: Functors are Data, so they have an IsValid() method
		if (not registered or not registered.IsValid()):
			logging.error(f"No valid object: {namespacedRegisteredName}")
			raise FatalCannotExecute(f"No valid object: {namespacedRegisteredName}")

		return registered


	# Non-static override of the SelfRegistering method.
	# Needed for errorObject resolution.
	@recoverable
	def RegisterAllClassesInDirectory(this, directory, recurse=True):
		path = Path(directory)
		if (not path.exists()):
			logging.debug(f"Making path for SelfRegitering classes: {str(path)}")
			path.mkdir(parents=True, exist_ok=True)

		if (directory not in this.syspath):
			this.syspath.append(directory)

		SelfRegistering.RegisterAllClassesInDirectory(directory, recurse=recurse)


	# Set a global value for use throughout all python modules.
	def SetGlobal(this, name, value, setFromFetch=False):
		# In cause the value was accessed with ".", we need to cast it to a DotDict.
		if (isinstance(value, dict)):
			value = util.DotDict(value)

		logging.debug(f"Setting global value {name} = {value}")
		setattr(builtins, name, value)
		this.globals.update({name: setFromFetch})


	# Move a value from Fetch to globals.
	def SetGlobalFromFetch(this, name):
		value = None
		isSet = False

		if (not isSet and this.globalContextKey):
			context = this.Fetch(this.globalContextKey)
			if (util.HasAttr(context, name)):
				value =  this.EvaluateToType(util.GetAttr(context, name))
				isSet = True

		if (not isSet):
			logging.debug(f"Fetching {name}...")
			val, fetched = this.FetchWithout(['globals', 'this'], name, start=False)
			if (fetched):
				value = this.EvaluateToType(val)
				isSet = True

		if (isSet):
			this.SetGlobal(name, value)
		else:
			logging.error(f"Failed to set global variable {name}")


	# Remove a variable from python's globals (i.e. builtins module)
	def ExpireGlobal(this, toExpire):
		logging.debug(f"Expiring global {toExpire}")
		try:
			delattr(builtins, toExpire)
		except Exception as e:
			logging.error(f"Failed to expire {toExpire}: {e}")
		# Carry on.


	# Remove all the globals *this has created.
	def ExpireAllGlobals(this):
		for gbl in this.globals.keys():
			this.ExpireGlobal(gbl)


	# Re-Fetch globals but leave manually set globals alone.
	def UpdateAllGlobals(this):
		logging.debug(f"Updating all globals")
		for gbl, fetch in this.globals.items():
			if (fetch):
				this.SetGlobalFromFetch(gbl)


	# Change the context key we use for fetching globals.
	# Then update globals.
	def SetGlobalContextKey(this, contextKey):
		updateGlobals = False
		if (this.globalContextKey != contextKey):
			updateGlobals = True

		logging.debug(f"Setting current config key to {contextKey}")
		this.globalContextKey = contextKey

		if (updateGlobals):
			this.UpdateAllGlobals()


	# Push a sub-context onto the current context
	def PushGlobalContextKey(this, keyToPush):
		this.SetGlobalContextKey(f"{this.globalContextKey}.{keyToPush}")


	# Pop a sub-context from the current context
	# The keyToPop must currently be the last key added.
	def PopGlobalContextKey(this, keyToPop):
		if (not this.globalContextKey.endswith(keyToPop)):
			raise GlobalError(f"{keyToPop} was not the last key pushed. Please pop {this.globalContextKey.split('.')[-1]} first.")
		this.globalContextKey = '.'.join(this.globalContextKey.split('.')[:-1])


	# Uses the ResolveError Functors to process any errors.
	@recoverable
	def ResolveError(this, error, attemptResolution, obj, function):
		if (attemptResolution >= len(this.error.resolvers)):
			raise FailedErrorResolution(f"{this.name} does not have {attemptResolution} resolutions to fix this error: {error} (it has {len(this.error.resolvers)})")

		resolution = this.GetRegistered(this.error.resolvers[attemptResolution], "resolve") # Okay to ResolveErrors for ErrorResolutions.
		this.error.resolution.stack, errorMightBeResolved = resolution(executor=this, error=error, obj=obj, function=function)
		if (errorMightBeResolved):
			logging.debug(f"Error might have been resolved by {resolution.name}.")
		return errorMightBeResolved


	######## START: Fetch Locations ########

	def fetch_location_args(this, varName, default, fetchFrom, attempted):
		for key, val in this.extraArgs.items():
			if (key == varName):
				return val, True
		return default, False

	######## END: Fetch Locations ########


# Global Fetch() function.
# Uses the latest registered Executor
def Fetch(varName, default=None, fetchFrom=None, start=True, attempted=None):
    return ExecutorTracker.GetLatest().Fetch(varName, default, fetchFrom, start, attempted)

# Ease-of-use wrapper for the global Fetch()
def f(varName, default=None, fetchFrom=None, start=True, attempted=None):
    Fetch(varName, default, fetchFrom, start, attempted)

class FetchCallbackFunctor(Functor):

	def __init__(this, name = "FetchCallbackFunctor"):
		super().__init__(name)

		this.arg.kw.required.append('varName')
		this.arg.kw.required.append('location')
		this.arg.kw.required.append('value')

		this.functionSucceeded = True
		this.feature.rollback = False

# Invoke the External Method machinery to fetch a Functor & return it.
# This should be used with other eons.kinds
class Inject(Functor):
	def __init__(this, name = "Inject"):
		super().__init__(name)
		this.arg.kw.required.append('target')
		this.arg.kw.optional['impl'] = 'External'

		this.arg.mapping.append('target')
		this.arg.mapping.append('impl')

		this.feature.autoReturn = False
	
	def Function(this):
		# Prepare a dummy function to replace with a Method.
		code = compile(f"def {this.target}(this):\n\tpass", '', 'exec')
		exec(code)

		methodToAdd = SelfRegistering(this.impl)
		methodToAdd.Constructor(eval(this.target), None)
		for key, value in this.kwargs.items():
			setattr(methodToAdd, key, value)

		return methodToAdd

def inject(
	target,
	impl="External",
	**kwargs
):
	return Inject()(target=target, impl=impl, **kwargs)


# AccessControl is used in Kind to control how Surfaces are created on a Functor & what is injected inside them.
# parameters should roughly map to the parameters result of inspect.signature().parameters
class AccessControl(Functor):
	def __init__(this, name = "AccessControl"):
		super().__init__(name)

		this.parameters = util.DotDict()

# Ease of use means of specifying a number of Methods to Inject
class PublicMethods(AccessControl):
	def __init__(this, name = "Public Methods"):
		super().__init__(name)

	def Function(this):
		toInject = {}

		# Functor doesn't allow arbitrary arg handling.
		# for arg in this.parameters:
		# 	toInject[arg] = arg

		for key, value in this.kwargs.items():
			toInject[key] = value
		
		for target, source in toInject.items():
			this.parameters[target] = util.DotDict({
				'kind': None,
				'name': target,
				'default': inject(source)
			})

def public_methods(*args, **kwargs):
	[kwargs.update({arg: arg}) for arg in args]
	return PublicMethods()(**kwargs)

def kind(
	base = StandardFunctor,
	**kwargs
):
	def ParseParameters(functor, args, source, ctor, strongType = False):
		# Code duplicated from Method.PopulateFrom. See that class for more info.
		for arg in args.values():
			if (arg.name == 'constructor' or arg.name == '__init__'):
				ctor.additions += f"{arg.default}\n"
				continue

			replaceWith = arg.name

			# *args
			if (arg.kind == inspect.Parameter.VAR_POSITIONAL):
				replaceWith = 'this.args'

			# **kwargs
			elif (arg.kind == inspect.Parameter.VAR_KEYWORD):
				replaceWith = 'this.kwargs'

			# Normal argument
			else:
				replaceWith = f'this.{arg.name}'
				shouldMapArg = arg.kind in [inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY]

				if (arg.default != inspect.Parameter.empty):
					if (isinstance(arg.default, Method)):
						arg.default.name = arg.name # Rename the Functor to match what was requested
						PrepareClassMethod(functor, arg.name, arg.default)
						shouldMapArg = False
					elif (isinstance(arg.default, AccessControl)):
						# NOTE: arg.name is discarded.
						functor, source, ctor = ParseParameters(
							functor,
							arg.default.parameters,
							source,
							ctor,
							strongType=strongType
						)
						shouldMapArg = False
					else:
						defaultValue = arg.default
						if (isinstance(arg.default, str)):
							defaultValue = f"'{arg.default}'"
						ctor.source.append(f"this.arg.kw.optional['{arg.name}'] = {defaultValue}")
				else:
					ctor.source.append(f"this.arg.kw.required.append('{arg.name}')")

				if (strongType and hasattr(arg, 'type')):
					ctor.source.append(f"""
	try:
		this.arg.type['{arg.name}'] = {arg.type.__name__}
	except:
		this.arg.type['{arg.name}'] = eons.SelfRegistering('{arg.type.__name__}')
""")

				if (shouldMapArg):
					ctor.source.append(f"this.arg.mapping.append('{arg.name}')")

			# Source mangling
			# TODO: Expand as we have more solid test cases.
			source = re.sub(fr"{arg.name}([\s\[\]\.\(\)\}}\*\+/-=%,]|$)", fr"{replaceWith}\1", source)
			
		return functor, source, ctor

	def FunctionToFunctor(function, functorName=None, args=None, source=None, strongType=False):
		executor = ExecutorTracker.GetLatest()
		shouldLog = executor and executor.verbosity > 3
		
		destinedModule = inspect.getmodule(function)
		destinedModuleName = INVALID_NAME()
		if (destinedModule):
			destinedModuleName = destinedModule.__name__
		pivotModule = None
		if (not destinedModule):
			pivotModule = inspect.currentframe().f_back
			if (not str(pivotModule).endswith('<module>>')):
				pivotModule = None

		bases = base
		if (isinstance(bases, type)):
			bases = [bases]
		
		primaryFunctionName = bases[0].primaryFunctionName

		if (functorName is None):
			functorName = function.__name__

		functor = type(
			functorName,
			(*bases,),
			{}
		)

		if ('name' not in kwargs):
			kwargs['name'] = functorName

		if (args is None):
			args = inspect.signature(function).parameters
		if (source is None):
			source = inspect.getsource(function)
		
		source = source[source.find(':\n')+1:].strip() # Will fail if an arg has ':\n' in it
		source = re.sub(r'epidef([\s\[\]\.\(\)\}\*\+/-=%,]|$)', r'this.epidef\1', source)

		ctor = util.DotDict()
		ctor.source = []
		ctor.additions = ""

		functor, source, ctor = ParseParameters(functor, args, source, ctor, strongType=strongType)

		# Constructor creation
		constructorName = f"_eons_constructor_{kwargs['name']}"
		constructorSource = f"def {constructorName}(this, name='{functorName}', **kwargs):"
		constructorSource += "\n\timport sys"
		constructorSource += "\n\timport eons"
		constructorSource += f'''
	this.name = name # For debugging
	try:
		{functor.__name__} = importedAs = eons.util.BlackMagick.GetCurrentFunction().__source_class__
		if (not isinstance(this, {functor.__name__})):
			raise Exception('{functor.__name__} not in source class')
	except Exception as e1:
		try:
			importedAs = eons.util.BlackMagick.GetCurrentFunction().__pivot_module__.f_locals['__imported_as__']
			{functor.__name__} = sys.modules[importedAs].{functor.__name__}
			if (not isinstance(this, {functor.__name__})):
				raise Exception('{functor.__name__} not in {{importedAs}}')
		except Exception as e2:
			try:
				{functor.__name__} = sys.modules[{destinedModuleName}].{functor.__name__}
				if (not isinstance(this, {functor.__name__})):
					raise Exception('{functor.__name__} not in {destinedModuleName}')
			except Exception as e3:
				logging.warning(f"Failed to initialize {functor.__name__}: \\n{{e1}}\\n{{e2}}\\n{{e3}}")
				# Catch all. This will cause an infinite loop if this != {functor.__name__}
				{functor.__name__} = this.__class__
	this.parent = type(this).mro()[1]
	super({functor.__name__}, this).__init__(**kwargs)
	this.name = name # For use
'''
		constructorSource += '\n\t' + '\n\t'.join(ctor.source)
		if (len(ctor.additions)):
			re.sub(r'^\s+', '\n', ctor.additions)
			constructorSource += '\n\t' + ('\n\t'.join(ctor.additions.split('\n'))).replace('self', 'this')
		if (shouldLog):
			logging.debug(f"Constructor source for {kwargs['name']}:\n{constructorSource}")
		code = compile(constructorSource, '', 'exec')
		exec(code)
		exec(f'functor.__init__ = {constructorName}')
		functor.__init__.__source_class__ = functor
		functor.__init__.__pivot_module__ = pivotModule

		wrappedPrimaryFunction = f"_eons_method_{kwargs['name']}"
		completeSource = f'''\
def {wrappedPrimaryFunction}(this):
	{source}
'''
		if (shouldLog):
			logging.debug(f"Primary function source for {kwargs['name']}:\n{completeSource}")
		code = compile(completeSource, '', 'exec')
		exec(code)
		exec(f'functor.{primaryFunctionName} = {wrappedPrimaryFunction}')

		return functor

	return FunctionToFunctor

