---
jupyter:
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  language_info:
    codemirror_mode:
      name: ipython
      version: 2
    file_extension: .py
    mimetype: text/x-python
    name: python
    nbconvert_exporter: python
    pygments_lexer: ipython2
    version: 2.7.6
  nbformat: 4
  nbformat_minor: 5
---

<div class="cell code" collapsed="false">

``` python
pip install neural-net-drawer
```

</div>

<div class="cell code" collapsed="false">

``` python
import matplotlib.pyplot as plt
from neural-net-drawer.drawer import NeuralNetworkDiagram()
```

</div>

<div class="cell code" execution_count="5"
ExecuteTime="{&quot;end_time&quot;:&quot;2024-02-07T08:56:55.425789900Z&quot;,&quot;start_time&quot;:&quot;2024-02-07T08:56:55.153634700Z&quot;}"
collapsed="false">

``` python
# Пример использования
fig = plt.figure(figsize=(9, 9))
ax = fig.gca()
ax.axis('off')

# Создание экземпляра класса
nn_diagram = NeuralNetworkDiagram()

# Вызов метода для построения диаграммы нейронной сети
nn_diagram.draw_neural_net(ax, [7, 5, 4, 3, 4, 2, 1])

plt.show()
```

<div class="output display_data">

![](img/1.png)

</div>

</div>

<div class="cell code" execution_count="13"
ExecuteTime="{&quot;end_time&quot;:&quot;2024-02-07T09:03:39.420467900Z&quot;,&quot;start_time&quot;:&quot;2024-02-07T09:03:39.268470Z&quot;}"
collapsed="false">

``` python
# Пример использования
fig = plt.figure(figsize=(9, 9))
ax = fig.gca()
ax.axis('off')

# Создание экземпляра класса
nn_diagram = NeuralNetworkDiagram()

#Максимальное количество отображаемых нейронов в сети
nn_diagram.max_n_layers_size = 3

#Максимальное количество отображаемых нейронов в сети.
nn_diagram.max_layer_size = 10


# Вызов метода для построения диаграммы нейронной сети
nn_diagram.draw_neural_net(ax, [7, 5, 4, 3, 4, 2, 1])

plt.show()
```

<div class="output display_data">

![](img/2.png)

</div>

</div>

<div class="cell code" execution_count="12"
ExecuteTime="{&quot;end_time&quot;:&quot;2024-02-07T09:01:57.191557900Z&quot;,&quot;start_time&quot;:&quot;2024-02-07T09:01:56.936069200Z&quot;}"
collapsed="false">

``` python
fig = plt.figure(figsize=(9, 9))
ax = fig.gca()
ax.axis('off')

# Создание экземпляра класса
nn_diagram = NeuralNetworkDiagram()
#Максимальное количество отображаемых нейронов в сети
nn_diagram.max_n_layers_size = 3

nn_diagram.show_neuron_numbers = False

# Вызов метода для построения диаграммы нейронной сети
nn_diagram.draw_neural_net(ax, [7, 5, 4, 3, 4, 2, 1])

plt.show()
```

<div class="output display_data">

![](img/3.png)

</div>

</div>
