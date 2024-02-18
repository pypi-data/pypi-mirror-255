import os
import subprocess
import time
import Oasys.gRPC


_connection = None
_debug      = False


def start(abspath, args=None, port=50054, memory=25, license=None, debug=False, batch=False):
    if debug:
        print("Starting {}, listening on port {}".format(abspath, port))

    environ = os.environ.copy()
    if license:
        environ[ARUP_LICENSE_PATH] = license

    pargs = [abspath, "-grpc={}".format(port)]
    if args:
        pargs.extend(args)
    if batch:
        pargs.append("-batch")

    subprocess.Popen(pargs, env=environ)

# Sleep to give time for D3PLOT to start
    time.sleep(5)

    return connect(port, memory, 'localhost', debug)


def connect(port=50052, memory=25, hostname='localhost', debug=False):
    if debug:
        print("Called connect with port {} and memory {}".format(port, memory))

    Oasys.D3PLOT._debug      = debug
    Oasys.D3PLOT._connection = Oasys.gRPC.Connection("D3PLOT", port, memory, hostname, debug)
    return Oasys.D3PLOT._connection


def disconnect(connection):
    if Oasys.D3PLOT._debug:
        print("Called disconnect")

    connection.finalise()
    Oasys.D3PLOT._connection = None


def terminate(connection):
    if Oasys.D3PLOT._debug:
        print("Called terminate")

    connection.terminate()
    Oasys.D3PLOT._connection = None


def createInstance(t, h):
# Classes in D3PLOT
    if t == "Beam":
        instance = object.__new__(Oasys.D3PLOT.Beam)
    elif t == "Colour":
        instance = object.__new__(Oasys.D3PLOT.Colour)
    elif t == "Component":
        instance = object.__new__(Oasys.D3PLOT.Component)
    elif t == "Constant":
        instance = object.__new__(Oasys.D3PLOT.Constant)
    elif t == "Contact":
        instance = object.__new__(Oasys.D3PLOT.Contact)
    elif t == "GraphicsWindow":
        instance = object.__new__(Oasys.D3PLOT.GraphicsWindow)
    elif t == "Group":
        instance = object.__new__(Oasys.D3PLOT.Group)
    elif t == "Image":
        instance = object.__new__(Oasys.D3PLOT.Image)
    elif t == "Include":
        instance = object.__new__(Oasys.D3PLOT.Include)
    elif t == "Material":
        instance = object.__new__(Oasys.D3PLOT.Material)
    elif t == "Measure":
        instance = object.__new__(Oasys.D3PLOT.Measure)
    elif t == "Model":
        instance = object.__new__(Oasys.D3PLOT.Model)
    elif t == "Node":
        instance = object.__new__(Oasys.D3PLOT.Node)
    elif t == "Options":
        instance = object.__new__(Oasys.D3PLOT.Options)
    elif t == "Page":
        instance = object.__new__(Oasys.D3PLOT.Page)
    elif t == "Part":
        instance = object.__new__(Oasys.D3PLOT.Part)
    elif t == "Segment":
        instance = object.__new__(Oasys.D3PLOT.Segment)
    elif t == "SetBeam":
        instance = object.__new__(Oasys.D3PLOT.SetBeam)
    elif t == "SetNode":
        instance = object.__new__(Oasys.D3PLOT.SetNode)
    elif t == "SetPart":
        instance = object.__new__(Oasys.D3PLOT.SetPart)
    elif t == "SetShell":
        instance = object.__new__(Oasys.D3PLOT.SetShell)
    elif t == "SetSolid":
        instance = object.__new__(Oasys.D3PLOT.SetSolid)
    elif t == "SetTshell":
        instance = object.__new__(Oasys.D3PLOT.SetTshell)
    elif t == "Shell":
        instance = object.__new__(Oasys.D3PLOT.Shell)
    elif t == "Solid":
        instance = object.__new__(Oasys.D3PLOT.Solid)
    elif t == "Tshell":
        instance = object.__new__(Oasys.D3PLOT.Tshell)
    elif t == "Type":
        instance = object.__new__(Oasys.D3PLOT.Type)
    elif t == "Utils":
        instance = object.__new__(Oasys.D3PLOT.Utils)
    elif t == "View":
        instance = object.__new__(Oasys.D3PLOT.View)
    elif t == "Window":
        instance = object.__new__(Oasys.D3PLOT.Window)
    elif t == "Workflow":
        instance = object.__new__(Oasys.D3PLOT.Workflow)

# Generic object
    elif t == "ItemObject":
        instance = object.__new__(Oasys.D3PLOT.ItemObject)

# Unsupported
    else:
        raise NotImplementedError("Instance type '{}' not implemented".format(t))

    instance.__dict__['_handle']  = h;
    instance.__dict__['_objtype'] = t;

    return instance
