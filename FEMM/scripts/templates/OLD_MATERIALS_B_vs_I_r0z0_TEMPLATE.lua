-- TEMPLATE -- ADJUST MATERIALS ETC HERE (BUT DO NOT RUN THIS FILE)
-- Author: Cole Kampa
-- 01-29-2021
-- Instructions: start FEMM, then load script: File->Open Lua Script

-- Some globals to change by hand
-- Magnet gap
gap = 75 -- mm

-- tempfile
tempfile = "temp_"..tostring(gap).."mm.fem"

-- set current range and increment and calculate step size
increment = 20 -- 10 -- 50 -- 20 -- 0.1
min_i = 0
max_i = 200 -- 140
steps = floor((max_i - min_i) / increment) + 1

-- file names
dir = "/home/ckampa/Coding/CalibMagnetCalc/FEMM/"
outfile = dir.."data/gap"..tostring(gap).."_B_vs_I_r0z0_results.txt"
geomfile = dir.."geom/GMW_"..tostring(gap).."mm.dxf"

-- Materials to use
mat_Env = "Air"
mat_Yoke = "416 stainless steel, annealed"
mat_Pole = "1010 Steel"
-- Custom materials to create
mat_Coil = "GMW Copper" -- custom material

-- Prepping the problem (pre-processor)
-- create magnetics file
newdocument(0)
-- save as temporary FEMM file
mi_saveas(tempfile)
-- Lua console
showconsole()
-- set problem type
mi_probdef(0, "millimeters", "axi", 1E-8)
-- grid size
mi_setgrid(10, "cart")
-- load DXF geometry (generated with python script)
mi_readdxf(geomfile) -- NOT WORKING (based on "OK" to tolerance?)
mi_zoomnatural()
-- define default circuit (140 A)
mi_addcircprop("Coil", 140, 1)
-- get desired materials from Materials Library
mi_getmaterial(mat_Env)
mi_getmaterial(mat_Yoke)
mi_getmaterial(mat_Pole)
-- define custom materials
--  args: name, mu_x, mu_y, H_c, J, Cduct, Lam_d, Phi_hmax, lam_fill,
--      LamType, Phi_hx, Phi_hy, NStrands, WireD
-- FIXME! Check LamType (along r or along z)
mi_addmaterial(mat_Coil, 1, 1, 0, 0, 58, 0.9116/2, 0,0.75,2,0,0,1,0) -- coil simple geom
-- mi_addmaterial("GMW Copper", 1, 1, 0, 0, 58, 0.9116, 0,0.75,2,0,0,1,0) -- with proper coil geom

--------------------
-- add labels: 1. add label at a position, 2. select label, 3. modify label
-- 7 labels (coils 1 geometry)
-- 9 labels if coils split properly
mi_seteditmode("blocks")
-- environment
-- inside
mi_addblocklabel(235,0)
mi_selectlabel(235,0)
mi_setblockprop(mat_Env, 1, 0, 0, 0, 0, 0)
mi_clearselected()
-- outside
mi_addblocklabel(550,0)
mi_selectlabel(550,0)
mi_setblockprop(mat_Env, 1, 0, 0, 0, 0, 0)
mi_clearselected()
-- coils
-- +z
mi_addblocklabel(235,170)
mi_selectlabel(235,170)
mi_setblockprop(mat_Coil, 1, 0, "Coil", 0, 0, 360)
mi_clearselected()
-- -z
mi_addblocklabel(235,-170)
mi_selectlabel(235,-170)
mi_setblockprop(mat_Coil, 1, 0, "Coil", 0, 0, 360)
mi_clearselected()
-- poles
-- +z
mi_addblocklabel(62,280)
mi_selectlabel(62,280)
mi_setblockprop(mat_Pole, 1, 0, 0, 0, 0, 0)
mi_clearselected()
-- -z
mi_addblocklabel(62,-280)
mi_selectlabel(62,-280)
mi_setblockprop(mat_Pole, 1, 0, 0, 0, 0, 0)
mi_clearselected()
-- yoke
mi_addblocklabel(380,0)
mi_selectlabel(380,0)
mi_setblockprop(mat_Yoke, 1, 0, 0, 0, 0, 0)
mi_clearselected()
--------------------

-- make boundary
mi_makeABC(7, 1000, 0, 0, 0)
-- zoom natural (should see boundary)
mi_zoomnatural()
-- create mesh
mi_createmesh()
-- zoom in 
mi_zoom(0, -500, 500, 500)

-- analyze for default current
mi_analyze()
mi_loadsolution()
-- refresh output view
mo_refreshview()
mo_maximize()
-- add colorful contour
mo_showdensityplot(1, 0, 2, 0, "bmag")
-- zooom
mo_zoom(0, -500, 500, 500)
-- pause for user check
pause()

-- save as temporary FEMM file
mi_saveas(tempfile)

-- MAIN CALCULATION (from v1)
-- write header and run info
handle=openfile(outfile,"w")
write(handle, "GMW Magnet with varying current, |B| @ r=z=0 (center of gap)\n")
write(handle, "Gap: ",tostring(gap),"mm\n")
write(handle, "Current Range: [",min_i,", ",max_i,"] Amps \n")
write(handle, "Current step size: ", increment, " Amps\n")
write(handle, "N_steps: ", steps, "\n")
write(handle, "Data is comma delimited\n")
write(handle, "Columns:\n")
write(handle, "I [A], B [T]\n")
closefile(handle)

-- loop through currents
for i=0,steps-1 do
	-- calculate current with equal increments
	current = i*increment + min_i
	-- adjust "Coil" circuit property 1 (current) to new value
	mi_modifycircprop("Coil",1,current)
	
	-- analyze with new current and load analyzed solution
	mi_analyze()
	mi_loadsolution()
	
	-- collect Br, Bz values from postprocessor
	_, Br, Bz, _, _, _, _, _, _, _, _, _, _ = mo_getpointvalues(0,0)
	B = sqrt(Br^2 + Bz^2)
	-- write B to file	
	handle=openfile(outfile,"a")
	write(handle, current, ', ', B, '\n')
	closefile(handle)
end
