import warnings
from typing import Optional
import matplotlib.pyplot as plt

from gempy.core.data import GeoModel
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
                  ve: float, series_n: Optional[list[int]], legend: bool = True, kwargs_topography: dict = None, kwargs_scalar_field: dict = None):
    legend_already_added = False

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
                    warnings.warn(
                        message='Section contacts not implemented yet. We need to pass scalar field for the sections grid',
                        category=UserWarning
                    )
                    pass
                    # plot_section_contacts()
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

        if legend and not legend_already_added:
            colors = gempy_model.structural_frame.elements_colors_contacts

            markers = [plt.Line2D([0, 0], [0, 0], color=color, marker='o', linestyle='') for color in colors]
            temp_ax.legend(
                markers,
                gempy_model.structural_frame.elements_names,
                numpoints=1
            )
            legend_already_added = True

            try:
                temp_ax.legend_.set_frame_on(True)
                temp_ax.legend_.set_zorder(10000)
            except AttributeError:
                pass
        
        if ve != 1:
            temp_ax.set_aspect(ve)
        
        # If there are section we need to shift one axis for the perpendicular
        e = e + 1

    return
