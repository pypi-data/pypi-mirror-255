<!-- markdownlint-disable -->

<a href="../../oqtant/schemas/optical.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `schemas.optical`






---

<a href="../../oqtant/schemas/optical.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Snapshot`
A class that represents a painted optical landscape/potential at a single point in (manipulation stage) time 


---

#### <kbd>property</kbd> interpolation_kind





---

#### <kbd>property</kbd> model_computed_fields

Get the computed fields of this model instance. 



**Returns:**
  A dictionary of computed field names and their corresponding `ComputedFieldInfo` objects. 

---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation. 



**Returns:**
  A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`. 

---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance. 



**Returns:**
  A set of strings representing the fields that have been set,  i.e. that were not filled from defaults. 



---

<a href="../../oqtant/schemas/optical.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_input`

```python
from_input(landscape: 'Landscape') → Snapshot
```

Method to create a Snapshot object from an existing jobs input 



**Args:**
 
 - <b>`landscape`</b> (bert_schemas.job.Landscape):  The input values 



**Returns:**
 
 - <b>`Snapshot`</b>:  A new Snapshot object created using the input data 

---

<a href="../../oqtant/schemas/optical.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(
    time: 'float' = 0,
    positions: 'list' = [-10, 10],
    potentials: 'list' = [0, 0],
    interpolation: 'InterpolationType' = 'LINEAR'
) → Snapshot
```

Method to create a new Snapshot object 



**Args:**
 
 - <b>`time`</b> (float, optional):  Time associated with the snapshot 
 - <b>`positions`</b> (list, optional):  Position list for the snapshot 
 - <b>`potentials`</b> (list, optional):  Potential energies corresponding to the list of positions 
 - <b>`interpolation`</b> (bert_schemas.job.InterpolationType, optional):  How to connect the object's  (positions, potentials) data in space. 



**Returns:**
 
 - <b>`Snapshot`</b>:  a new Snapshot object 

---

<a href="../../oqtant/schemas/optical.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `show_potential`

```python
show_potential(
    xlimits: 'list[float]' = [-61.0, 61],
    ylimits: 'list[float]' = [-1.0, 101],
    include_ideal: 'bool' = False
) → None
```

Method to plot the potential energy as a function of position for a Landscape object at the given times 



**Args:**
 
 - <b>`xlimits`</b> (list[float], optional):  Plot limits for x axis 
 - <b>`ylimits`</b> (list[float], optional):  Plot limits for y axis 
 - <b>`include_ideal`</b> (bool, optional):  Flag for including target potential in plot 


---

<a href="../../oqtant/schemas/optical.py#L120"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Landscape`
Class that represents a dynamic painted-potential optical landscape constructed from individual (instantaneous time) Snapshots 


---

#### <kbd>property</kbd> interpolation_kind





---

#### <kbd>property</kbd> model_computed_fields

Get the computed fields of this model instance. 



**Returns:**
  A dictionary of computed field names and their corresponding `ComputedFieldInfo` objects. 

---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation. 



**Returns:**
  A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`. 

---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance. 



**Returns:**
  A set of strings representing the fields that have been set,  i.e. that were not filled from defaults. 

---

#### <kbd>property</kbd> snapshots

Property to get a list of Snapshot objects associated to a Landscape object 



**Returns:**
 
 - <b>`list[Snapshot]`</b>:  List of Snapshot objects 



---

<a href="../../oqtant/schemas/optical.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_input`

```python
from_input(landscape: 'OpticalLandscape') → Landscape
```

Method to create a Landscape object from an existing jobs input 



**Args:**
 
 - <b>`landscape`</b> (job_schema.OpticalLandscape):  The input values 



**Returns:**
 
 - <b>`Landscape`</b>:  A new Landscape object 

---

<a href="../../oqtant/schemas/optical.py#L125"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(
    snapshots: 'list[Snapshot]' = [Snapshot(time_ms=0.0, potentials_khz=[0.0, 0.0], positions_um=[-10.0, 10.0], spatial_interpolation=<InterpolationType.LINEAR: 'LINEAR'>, interpolation_kind='linear'), Snapshot(time_ms=2.0, potentials_khz=[0.0, 0.0], positions_um=[-10.0, 10.0], spatial_interpolation=<InterpolationType.LINEAR: 'LINEAR'>, interpolation_kind='linear')]
) → Landscape
```

Method to create a new Landscape object 



**Args:**
 
 - <b>`snapshots`</b> (list[Snapshot], optional):  A list of Snapshot objects 



**Returns:**
 
 - <b>`Landscape`</b>:  A new Landscape object 

---

<a href="../../oqtant/schemas/optical.py#L175"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `show_potential`

```python
show_potential(
    times: 'list' = [0.0],
    xlimits: 'list' = [-61.0, 61],
    ylimits: 'list' = [-1.0, 101],
    include_ideal: 'bool' = False
)
```

Method to plot the potential energy as a function of position for a Landscape object at the given times 



**Args:**
 
 - <b>`times`</b> (list[float], optional):  Times, in ms, at which to evaluate and plot the potential 
 - <b>`xlimits`</b> (list[float], optional):  Plot limits for x axis 
 - <b>`ylimits`</b> (list[float], optional):  Plot limits for y axis 
 - <b>`include_ideal`</b> (bool, optional):  Flag for including target potential in plot 


---

<a href="../../oqtant/schemas/optical.py#L220"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Barrier`
Class that represents a painted optical barrier. 


---

#### <kbd>property</kbd> birth

Property to get the (manipulation stage) time that the Barrier object will be created 



**Returns:**
 
 - <b>`float`</b>:  The time, in ms, at which the barrier will start being projected 

---

#### <kbd>property</kbd> death

Property to get the (manipulation stage) time that the Barrier object will cease to exist 



**Returns:**
 
 - <b>`float`</b>:  The time, in ms, at which the barrier will stop being projected 

---

#### <kbd>property</kbd> interpolation_kind





---

#### <kbd>property</kbd> lifetime

Property to get the lifetime value of a Barrier object 



**Returns:**
 
 - <b>`float`</b>:  The amount of time, in ms, that the barrier will exist 

---

#### <kbd>property</kbd> model_computed_fields

Get the computed fields of this model instance. 



**Returns:**
  A dictionary of computed field names and their corresponding `ComputedFieldInfo` objects. 

---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation. 



**Returns:**
  A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`. 

---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance. 



**Returns:**
  A set of strings representing the fields that have been set,  i.e. that were not filled from defaults. 



---

<a href="../../oqtant/schemas/optical.py#L265"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_input`

```python
from_input(barrier: 'Barrier') → Barrier
```

Method to create a Barrier object using the input values of a job 



**Args:**
 
 - <b>`barrier`</b> (job_schema.Barrier):  The input values 



**Returns:**
 
 - <b>`Barrier`</b>:  A new Barrier object created using the input data 

---

<a href="../../oqtant/schemas/optical.py#L223"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(
    positions: 'list[float]' = [0.0, 0.0],
    heights: 'list[float]' = [0.0, 0.0],
    widths: 'list[float]' = [1.0, 1.0],
    times: 'list[float]' = [0.0, 10.0],
    shape: 'ShapeType' = <ShapeType.GAUSSIAN: 'GAUSSIAN'>,
    interpolation: 'InterpolationType' = <InterpolationType.LINEAR: 'LINEAR'>
) → Barrier
```

Method to create a new Barrier object 



**Args:**
 
 - <b>`positions`</b> (list[float], optional):  Positions for the barrier 
 - <b>`heights`</b> (list[float], optional):  Heights for the barrier 
 - <b>`widths`</b> (list[float], optional):  Widths for the barrier 
 - <b>`times`</b> (list[float], optional):  Times for the barrier 
 - <b>`shape`</b> (bert_schemas.job.ShapeType, optional):  Shape of the barrier 
 - <b>`interpolation`</b> (bert_schemas.job.InterpolationType, optional):  Interpolation type of the barrier 



**Returns:**
 
 - <b>`Barrier`</b>:  A new Barrier object 



**Raises:**
 
 - <b>`ValueError`</b>:  if data lists are not of equal length 

---

<a href="../../oqtant/schemas/optical.py#L277"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `show_dynamics`

```python
show_dynamics() → None
```

Method to plot the position, width and height of a Barrier object over time 

---

<a href="../../oqtant/schemas/optical.py#L324"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `show_potential`

```python
show_potential(
    times: 'list[float]' = [0.0],
    xlimits: 'list[float]' = [-61.0, 61],
    ylimits: 'list[float]' = [-1.0, 101],
    include_ideal: 'bool' = False
) → None
```

Method to plot the potential energy as a function of position for a Barrier object 



**Args:**
 
 - <b>`times`</b> (list[float], optional):  The times, in ms, at which the potential is evaluated 
 - <b>`xlimits`</b> (list[float], optional):  Plot limits for x axis 
 - <b>`ylimits`</b> (list[float], optional):  Plot limits for y axis 
 - <b>`include_ideal`</b> (bool, optional):  Flag for including target potential in plot 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
