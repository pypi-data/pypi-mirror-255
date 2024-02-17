from typing import Union, List, overload, Optional, Tuple, Literal
from dataclasses import dataclass

from ..charts import LineChart
from ..controllers import Table
from ..widget import Widget, AttributeNames

JustifyLiteral = Literal['start', 'center', 'end', 'space-between', 'space-around', 'space-evenly']

AlignLiteral = Literal['top', 'middle', 'bottom']


@dataclass
class _Column(Widget):
    def __init__(self, item: Widget, offset: int, span: int) -> None:
        super().__init__('ContainerCol')
        self.__item = item
        self.__offset = offset
        self.__span = span
        
    def to_dict_widget(self, host: str = None):
        as_dict = super().to_dict_widget()
        as_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.COL_OFFSET.value: self.__offset,
            AttributeNames.COL_SPAN.value: self.__span,
            AttributeNames.WIDGETS.value: [
                self.__item.to_dict_widget(host) if isinstance(self.__item, (LineChart, Table)) 
                else self.__item.to_dict_widget()
            ]
        })
        return as_dict

class _Row(Widget):
    def __init__(self, columns: List[_Column], justify: JustifyLiteral, align: AlignLiteral) -> None:
        super().__init__('ContainerRow')
        self.__columns = columns
        self.__justify = justify
        self.__align = align
        
    def to_dict_widget(self, host: str = None):
        as_dict = super().to_dict_widget()
        as_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.JUSTIFY.value: self.__justify,
            AttributeNames.ALIGN.value: self.__align,
            AttributeNames.WIDGETS.value: [c.to_dict_widget(host) for c in self.__columns] 
        })
        
        return as_dict

class Container(Widget):
    """
    Common methods to place controls in a container
    """

    def __init__(self, **kwargs) -> None:
        super().__init__('Container', **kwargs)
        # __rows contains a list of lists, each one representing
        # a row where components and distributed among 24 logical
        # columns.
        self.__rows: List[List[_Row]] = []

    def to_dict_widget(self, host: str = None):
        as_dict = super().to_dict_widget()
        as_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.WIDGETS.value: [r.to_dict_widget(host) for r in self.__rows] 
        })
        return as_dict

    @overload
    def place(self, inner: Widget,
              width: Optional[Union[int, Tuple[int, int]]] = None,
              *,
              justify: JustifyLiteral = 'start',
              align: AlignLiteral = 'top') -> None:
        """
        Places a single component within a container.

        Notes
        -----
        When `width` parameter is not given the inner component will occupy
        all available space. 

        When `width` provides a single integer, it denotes the amount of 
        logical columns the components occupies; the total horizontal space
        is divided in 24 even columns.

        When `width` is given by a tuple of integers, the first parameter 
        denotes the amount of blank space to the left of the component; the 
        second tuple value denotes the actual width.

        Example, to center a component within a container, leaving just one 
        blank space to the left and right, the width parameter will be given 
        as `(1,22)`, that is, 1 column of blank space, followed 
        by the component of size 22; the remainder column to the right of the 
        component will be set to blank, as the total sum should be equal to 24.  

        One can choose any combination of values to center the component, as 
        long as the total sum of columns allocated doesn't go over 24.

        Examples
        --------
        * One third of the space, aligned to the right: `(16,8)`
        * Centered, all spaces equal: `(8,8)`
        * One third of the space, aligned to the left: `8`

        Parameters
        ----------
        inner: Widget
            The component to place

        width: int|(int,int), optional, Defaults to None.
            Determines the width and the blank space occupied by a single 
            component

        justify: str literal; one of 'start' (default), 'center', 'end', 'space-between', 'space-around', 'space-evenly'
            Determines how the empty space will be distributed horizontally, where:

                - `start`, aligns the component to the left hand side of the container.
                - `center`, centers the component horizontally.
                - `end`, aligns the component to the right hand side of the container.
                - the rest of the options are equivalent to center to the case of a 
                  single widget.

        align: str literal; one of 'top', 'middle', 'bottom'
            Determines how the widget is aligned vertically within the container.            
        """
        ...

    @overload
    def place(self, innerList: List[Widget],
              widths: Optional[List[Union[int, Tuple[int, int]]]] = None,
              *,
              justify: JustifyLiteral = 'start',
              align: AlignLiteral = 'top') -> None:
        """
        Places components within a container on a new row.

        Notes
        -----
        The components will occupy all the available horizontal space as per
        the distribution set by the parameter `width`.  When `width` is not 
        set, all components will distribute evenly.

        `width` parameter should be of the same size as the number of elements
        provided in `innerList` parameter.

        `width` parameter is expected to be a list of integers or tuples of two
        integers, and all values are expected to sum a maximum of 24, which is 
        the number of logical columns dividing the horizontal space.  If the values 
        sum less than 24, the unallocated space will be blank space to the right 
        most component.

        When an item in `width` is specified as integer, it will denote how many of 
        the 24 logical columns that divide the horizontal space should be used for 
        the corresponding inner component; if the `width` item is given by a tuple,
        the first element of the tuple will be considered as an blank offset to the
        left of the component.  

        Parameters
        ----------
        innerList: List[Widget], required
            List of inner components to distribute on a new row.

        widths: [int|(int,int)], optional, defaults to None.
            Optional parameter that specifies, for each component in `innerList`, the 
            amount of space each component is given in relation to the available space.  
            The available space is divided on 24 columns of equal size.  

        justify: str literal; one of 'start' (default), 'center', 'end', 'space-between', 'space-around', 'space-evenly'
            Determines how the empty space will be distributed horizontally, where:

            - `start`, places all components next to each other to the left hand side of the container.  
            - `center`, places all components next to each other and centers the group within the container.  
            - `end`, similarly to `start` and `center`, but to the right hand side of the container.
            - `space-between`, places the first widget to the left hand side of the container and the last 
            one is aligned right end.  The rest of the components are spread within the container, all of 
            them with equal blank spaces. 
            - `space-around`, similarly to `space-between` spreads all components within available container 
            space space but, as difference to the previous settings, there will be a blank area at the 
            rightmost and leftmost borders of the container, which is half of the space between two components.  
            - `space-evenly`, same as before, but all empty spaces have equal width.

        align: str literal; one of 'top', 'middle', 'bottom'
            Determines how the widget is aligned vertically within the container.

        """
        ...

    def place(self, *args, **kwargs) -> None:
        # check parameters
        if len(args) == 0:
            raise ValueError('place expects one component or a list of components')

        if len(args) > 2:
            raise ValueError(f'place expects at most two parameters; called with {len(args)}')

        # ensure the first parameter is a list
        innerList = args[0]
        if not isinstance(innerList, list):
            innerList = [innerList]

        # validate all entries in inner list are valid
        for c in innerList:
            if not isinstance(c, Widget):
                raise TypeError(f'place expects elements of type Widget; given {type(c)}')

        # check widths...
        width: List[Tuple[int, int]] = []
        if len(args) == 1:
            # no width parameter specified, divide by all space evenly
            if len(innerList) > 24:
                raise ValueError(f'A container may have, at most, 24 elements; given {len(innerList)}')
            # do a quick allocation assuming no blank space.
            width = [(0, 24 // len(innerList))] * len(innerList)

        else:
            # width parameter is given
            unchecked_width = args[1]
            if not isinstance(unchecked_width, list):
                unchecked_width = [unchecked_width]

            if len(unchecked_width) != len(innerList):
                raise ValueError(f'Inner component count {len(innerList)} should match `width` counts {len(unchecked_width)}')

            acc = 0
            for entry in unchecked_width:
                if isinstance(entry, int):
                    acc += entry
                    width.append((0, entry))
                elif isinstance(entry, tuple) and len(entry) == 2 and all(isinstance(i, int) for i in entry):
                    acc += entry[0]
                    acc += entry[1]
                    width.append(entry)
                else:
                    raise ValueError(f'Invalid `width` parameter: {entry}')

            if acc > 24:
                raise ValueError(f'place supports at most 24 columns; given {acc}')

        # now that we have verified all parameters, simply
        # update __rows by adding a new row configuration.
        columns = [_Column(c, w[0], w[1]) for (c, w) in zip(innerList, width)]
        row = _Row(columns, kwargs.get('justify', 'start'), kwargs.get('align', 'top'))
        self.__rows.append(row)

    def place_grid(self,
                   rows: List[Union[Widget, List[Widget]]],
                   *,
                   justify: JustifyLiteral = 'start',
                   align: AlignLiteral = 'top') -> None:
        """
        Places components automatically on a grid structure

        Notes
        -----
        The number of elements on the outer list determines the 
        number of rows to place; each row is a list of controls 
        to be distributed evenly.

        `justify` and `align` applies to all rows in the grid.

        Parameters
        ----------
        children: List[Child|List[Child]], required
            Array of Arrays containing the elements to be placed in the grid.

        justify: str literal; one of 'start' (default), 'center', 'end', 'space-between', 'space-around', 'space-evenly'
            Determines how the empty space will be distributed horizontally among rows, where:

            - `start`, places all components next to each other to the left hand side of the container.  
            - `center`, places all components next to each other and centers the group within the container.  
            - `end`, similarly to `start` and `center`, but to the right hand side of the container.
            - `space-between`, places the first widget to the left hand side of the container and the last 
            one is aligned right end.  The rest of the components are spread within the container, all of 
            them with equal blank spaces. 
            - `space-around`, similarly to `space-between` spreads all components within available container 
            space space but, as difference to the previous settings, there will be a blank area at the 
            rightmost and leftmost borders of the container, which is half of the space between two components.  
            - `space-evenly`, same as before, but all empty spaces have equal width.

        align: str literal; one of 'top', 'middle', 'bottom'
            Determines how the widget is aligned vertically within the container.            

        """
        for row in rows:
            self.place(row, justify=justify, align=align)
