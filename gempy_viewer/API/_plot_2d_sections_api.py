from ..modules.plot_2d.drawer_contours_2d import plot_contacts
from ..modules.plot_2d.drawer_scalar_field_2d import plot_scalar_field
from ..modules.plot_2d.drawer_input_2d import plot_data
from ..modules.plot_2d.drawer_regular_grid_2d import plot_regular_grid


def _plot_regular_grid_section(
        cell_number, direction, e, kwargs, kwargs_regular_grid, kwargs_topography,
        model, n_axis, n_columns, p, regular_grid, series_n, show_block, show_boundaries, show_data, show_lith,
        show_scalar, show_topography, show_values, ve):
    for e2 in range(len(cell_number)):
        assert (e + e2) < 10, 'Reached maximum of axes'
        
        # region prepare axis
        temp_ax = p.add_section(
            gempy_grid=model.grid,
            cell_number=cell_number[e2],
            direction=direction[e2],
            ax_pos=((round(n_axis / 2 + 0.1)) * 100 + n_columns + e + e2 + 1),
            ve=ve
        )
        # endregion
        
        # region plot data
        if show_data[e + e2] is True:
            plot_data(
                plot_2d=p,
                gempy_model=model,
                ax=temp_ax,
                cell_number=cell_number[e2],
                direction=direction[e2],
                **kwargs
            )
        if show_topography[e + e2] is True:
            p.plot_topography(temp_ax, cell_number=cell_number[e2],
                              direction=direction[e2], **kwargs_topography)
        # endregion
        
        # region plot solutions
        if show_lith[e + e2] is True and model.solutions.raw_arrays.lith_block.shape[0] != 0:
            plot_regular_grid(
                plot_2d=p,
                gempy_model=model,
                ax=temp_ax,
                block=model.solutions.raw_arrays.lith_block,
                resolution=model.grid.regular_grid.resolution,
                cell_number=cell_number[e2],
                direction=direction[e2],
            )
        elif show_values[e + e2] is True and model.solutions.raw_arrays.values_matrix.shape[0] != 0:
            p.plot_values(temp_ax, series_n=series_n[e], cell_number=cell_number[e2],
                          direction=direction[e2], **kwargs)
        elif show_block[e + e2] is True and model.solutions.raw_arrays.block_matrix.shape[0] != 0:
            p.plot_block(temp_ax, series_n=series_n[e], cell_number=cell_number[e2],
                         direction=direction[e2], **kwargs)
        if show_scalar[e + e2] is True and model.solutions.raw_arrays.scalar_field_matrix.shape[0] != 0:
            plot_scalar_field(
                plot_2d=p,
                gempy_model=model,
                ax=temp_ax,
                block=model.solutions.raw_arrays.scalar_field_matrix[series_n],
                resolution=model.grid.regular_grid.resolution,
                cell_number=cell_number[e2],
                direction=direction[e2],
                series_n=series_n
            )
            
        if show_boundaries[e + e2] is True and model.solutions.raw_arrays.scalar_field_matrix.shape[0] != 0:
            plot_contacts(
                plot_2d=p,
                gempy_model=model,
                ax=temp_ax,
                resolution=model.grid.regular_grid.resolution,
                cell_number=cell_number[e2],
                direction=direction[e2],
                only_faults=False
            )
            
        # endregion
        # region passed regular grid
        # ? This here is funny
        if regular_grid is not None:
            p.plot_regular_grid(temp_ax, block=regular_grid, cell_number=cell_number[e2],
                                direction=direction[e2], **kwargs_regular_grid)
        # endregion
        temp_ax.set_aspect(ve)


def _plot_section_grid(kwargs, kwargs_regular_grid, kwargs_topography, model, n_axis, n_columns, p, regular_grid, section_names, series_n, show_block, show_boundaries, show_data, show_lith, show_scalar, show_section_traces, show_topography, show_values, ve):
    e = 0
    for e, sn in enumerate(section_names):

        # region matplotlib configuration
        # Check if a plot that fills all pixels is plotted
        _is_filled = False
        assert e < 10, 'Reached maximum of axes'

        ax_pos = (round(n_axis / 2 + 0.1)) * 100 + n_columns + e + 1
        temp_ax = p.add_section(section_name=sn, ax_pos=ax_pos, ve=ve, **kwargs)
        # endregion 

        # TODO: (miguel Jun 2023) can I start to replace these methods for functions one by one? 
        # region plot methods
        if show_data[e] is True:
            p.plot_data(temp_ax, section_name=sn, **kwargs)
        if show_lith[e] is True and model.solutions.lith_block.shape[0] != 0:
            _is_filled = True
            p.plot_lith(temp_ax, section_name=sn, **kwargs)
        elif show_values[e] is True and model.solutions.values_matrix.shape[0] != 0:
            _is_filled = True
            p.plot_values(temp_ax, series_n=series_n[e], section_name=sn, **kwargs)
        elif show_block[e] is True and model.solutions.block_matrix.shape[0] != 0:
            _is_filled = True
            p.plot_block(temp_ax, series_n=series_n[e], section_name=sn, **kwargs)
        if show_scalar[e] is True and model.solutions.scalar_field_matrix.shape[0] != 0:
            _is_filled = True
            p.plot_scalar_field(temp_ax, series_n=series_n[e], section_name=sn, **kwargs)
        if show_boundaries[e] is True and model.solutions.scalar_field_matrix.shape[0] != 0:
            p.plot_contacts(temp_ax, section_name=sn, **kwargs)
        if show_topography[e] is True:
            # Check if anything dense is plot. If not plot dense topography
            f_c_ = not _is_filled
            # f_c = kwargs_topography.get('fill_contour', f_c_)
            if 'fill_contour' not in kwargs_topography:
                kwargs_topography['fill_contour'] = f_c_
            p.plot_topography(temp_ax, section_name=sn,  # fill_contour=f_c,
                              **kwargs_topography)
            if show_section_traces is True and sn == 'topography':
                p.plot_section_traces(temp_ax)

        if regular_grid is not None:
            p.plot_regular_grid(temp_ax, block=regular_grid, section_name=sn,
                                **kwargs_regular_grid)

        # endregion
        temp_ax.set_aspect(ve)

        # If there are section we need to shift one axis for the perpendicular
        e = e + 1

    return e
