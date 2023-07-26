from typing import Optional

from gempy import GeoModel
from gempy_viewer.core.section_data_2d import SectionData2D, SectionType
from gempy_viewer.core.data_to_show import DataToShow
from ..modules.plot_2d.plot_2d_utils import get_geo_model_cmap, get_geo_model_norm
from ..modules.plot_2d.drawer_traces_2d import plot_section_traces
from ..modules.plot_2d.drawer_topography_2d import plot_topography
from ..modules.plot_2d.drawer_contours_2d import plot_section_contacts, plot_regular_grid_contacts
from ..modules.plot_2d.drawer_input_2d import draw_data
from ..modules.plot_2d.drawer_regular_grid_2d import plot_section_area, plot_regular_grid_area
from ..modules.plot_2d.drawer_scalar_field_2d import plot_section_scalar_field, plot_regular_grid_scalar_field



def plot_sections(gempy_model: GeoModel, sections_data: list[SectionData2D], data_to_show: DataToShow,
                  series_n: Optional[list[int]], kwargs_topography: dict = None, kwargs_scalar_field: dict = None):
    for e, section_data in enumerate(sections_data):
        temp_ax = section_data.ax
        # region plot methods
        if data_to_show.show_data[e] is True:
            draw_data(
                ax=temp_ax,
                surface_points_colors=gempy_model.structural_frame.surface_points_colors,
                orientations_colors=gempy_model.structural_frame.orientations_colors,
                orientations=gempy_model.orientations.df.copy(),
                points=gempy_model.surface_points.df.copy(),
                slicer_data=section_data.slicer_data
            )

        if data_to_show.show_lith[e] is True:
            _is_filled = True
            match section_data.section_type:
                case SectionType.SECTION:
                    plot_section_area(
                        gempy_model=gempy_model,
                        ax=temp_ax,
                        section_name=section_data.section_name,
                        cmap=get_geo_model_cmap(gempy_model.structural_frame.elements_colors),
                        norm=get_geo_model_norm(gempy_model.structural_frame.number_of_elements),
                    )
                case SectionType.ORTHOGONAL:
                    plot_regular_grid_area(
                        ax=temp_ax,
                        slicer_data=section_data.slicer_data,
                        block=gempy_model.solutions.raw_arrays.lith_block,  # * Only used for orthogonal sections
                        resolution=gempy_model.grid.regular_grid.resolution,
                        cmap=get_geo_model_cmap(gempy_model.structural_frame.elements_colors),
                        norm=get_geo_model_norm(gempy_model.structural_frame.number_of_elements),
                    )
                case _:
                    raise ValueError(f'Unknown section type: {section_data.section_type}')
        # TODO: Revive the other solutions
        # elif data_to_show.show_values[e] is True: # and model.solutions.values_matrix.shape[0] != 0:
        #     _is_filled = True
        #     p.plot_values(temp_ax, series_n=series_n[e], section_name=sn, **kwargs)
        # elif show_block[e] is True and model.solutions.block_matrix.shape[0] != 0:
        #     _is_filled = True
        #     p.plot_block(temp_ax, series_n=series_n[e], section_name=sn, **kwargs)
        if data_to_show.show_scalar[e] is True:
            _is_filled = True
            match section_data.section_type:
                case SectionType.SECTION:
                    plot_section_scalar_field(
                        gempy_model=gempy_model,
                        ax=temp_ax,
                        section_name=section_data.section_name,
                        series_n=series_n[e],
                        kwargs=kwargs_scalar_field
                    )
                case SectionType.ORTHOGONAL:
                    plot_regular_grid_scalar_field(
                        ax=temp_ax,
                        slicer_data=section_data.slicer_data,
                        block=gempy_model.solutions.raw_arrays.scalar_field_matrix[series_n[e]],
                        resolution=gempy_model.grid.regular_grid.resolution,
                        kwargs=kwargs_scalar_field
                    )
                case _:
                    raise ValueError(f'Unknown section type: {section_data.section_type}')
        if data_to_show.show_boundaries[e] is True:
            match section_data.section_type:
                case SectionType.SECTION:
                    raise NotImplementedError('Section contacts not implemented yet')
                    plot_section_contacts()
                case SectionType.ORTHOGONAL:
                    plot_regular_grid_contacts(
                        gempy_model=gempy_model,
                        ax=temp_ax,
                        slicer_data=section_data.slicer_data,
                        resolution=gempy_model.grid.regular_grid.resolution,
                        only_faults=False,
                        kwargs=kwargs_topography
                    )
                case _:
                    raise ValueError(f'Unknown section type: {section_data.section_type}')

        if data_to_show.show_topography[e] is True:
            plot_topography(
                gempy_model=gempy_model,
                ax=temp_ax,
                fill_contour=kwargs_topography.get('fill_contour', True),
                section_name=section_data.section_name,
                **kwargs_topography
            )

            if data_to_show.show_section_traces is True and section_data.section_name == 'topography':
                plot_section_traces(
                    gempy_model=gempy_model,
                    ax=temp_ax,
                    section_names=[section_data.section_name for section_data in sections_data],
                )

        # ? This was just to plot directly a 2d array... mmmm not sure what to do with this
        # if regular_grid is not None:
        #     p.plot_regular_grid(temp_ax, block=regular_grid, section_name=sn,
        #                         **kwargs_regular_grid)
        # 
        # # endregion
        # temp_ax.set_aspect(ve)

        # If there are section we need to shift one axis for the perpendicular
        e = e + 1

    return


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
                direction=direction[e2]
            )
        if show_topography[e + e2] is True:
            plot_topography(
                gempy_model=model,
                ax=temp_ax,
                fill_contour=kwargs_topography.get('fill_contour', True),
                cell_number=cell_number[e2],
                direction=direction[e2],
                **kwargs_topography
            )

            # p.plot_topography(temp_ax, cell_number=cell_number[e2],
            #                   direction=direction[e2], **kwargs_topography)
        # endregion

        # region plot solutions
        if show_lith[e + e2] is True and model.solutions.raw_arrays.lith_block.shape[0] != 0:
            plot_regular_grid(
                ax=temp_ax,
                block=model.solutions.raw_arrays.lith_block,
                resolution=model.grid.regular_grid.resolution,
            )
        elif show_values[e + e2] is True and model.solutions.raw_arrays.values_matrix.shape[0] != 0:
            p.plot_values(temp_ax, series_n=series_n[e], cell_number=cell_number[e2],
                          direction=direction[e2], **kwargs)
        elif show_block[e + e2] is True and model.solutions.raw_arrays.block_matrix.shape[0] != 0:
            p.plot_block(temp_ax, series_n=series_n[e], cell_number=cell_number[e2],
                         direction=direction[e2], **kwargs)
        if show_scalar[e + e2] is True and model.solutions.raw_arrays.scalar_field_matrix.shape[0] != 0:
            plot_scalar_field(
                gempy_model=model,
                ax=temp_ax,
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
        

def _plot_section_grid(kwargs, kwargs_regular_grid, kwargs_topography, model, n_axis,
                       n_columns, p, regular_grid, section_names, series_n, show_block,
                       show_boundaries, show_data, show_lith, show_scalar,
                       show_section_traces, show_topography, show_values, ve):
    e = 0
    for e, sn in enumerate(section_names):

        # region matplotlib configuration
        # Check if a plot that fills all pixels is plotted
        _is_filled = False
        assert e < 10, 'Reached maximum of axes'

        ax_pos = (round(n_axis / 2 + 0.1)) * 100 + n_columns + e + 1
        temp_ax = p.add_section(
            gempy_grid=model.grid,
            section_name=sn,
            ax_pos=ax_pos,
            ve=ve,
            **kwargs
        )
        # endregion 

        # TODO: (miguel Jun 2023) can I start to replace these methods for functions one by one? 
        # region plot methods
        if show_data[e] is True:
            # p.plot_data(temp_ax, section_name=sn, **kwargs)

            plot_data(
                plot_2d=p,
                gempy_model=model,
                ax=temp_ax,
                section_name=sn
            )
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
            plot_topography(
                gempy_model=model,
                ax=temp_ax,
                fill_contour=kwargs_topography.get('fill_contour', True),
                section_name=sn,
                **kwargs_topography
            )
            # p.plot_topography(temp_ax, section_name=sn,  # fill_contour=f_c,
            #                   **kwargs_topography)
            if show_section_traces is True and sn == 'topography':
                plot_section_traces(
                    gempy_model=model,
                    ax=temp_ax,
                    section_names=section_names,
                )
                # p.plot_section_traces(temp_ax)

        if regular_grid is not None:
            p.plot_regular_grid(temp_ax, block=regular_grid, section_name=sn,
                                **kwargs_regular_grid)

        # endregion
        temp_ax.set_aspect(ve)

        # If there are section we need to shift one axis for the perpendicular
        e = e + 1

    return e
