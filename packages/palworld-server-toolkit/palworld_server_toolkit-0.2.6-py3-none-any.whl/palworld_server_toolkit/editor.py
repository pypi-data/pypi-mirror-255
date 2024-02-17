#!/usr/bin/env python3
# Author: MagicBear
# License: MIT License
import json
import os, datetime, time
import sys
import threading
import pprint
import tkinter.font
import uuid
import argparse
import copy
import importlib.metadata

import tkinter as tk
import tkinter.font
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog

module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, module_dir)
sys.path.insert(0, os.path.join(module_dir, "../"))
sys.path.insert(0, os.path.join(module_dir, "PalEdit"))
# sys.path.insert(0, os.path.join(module_dir, "../save_tools"))
# sys.path.insert(0, os.path.join(module_dir, "../palworld-save-tools"))

from palworld_save_tools.gvas import GvasFile
from palworld_save_tools.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from palworld_save_tools.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS
from palworld_save_tools.archive import *

from palworld_server_toolkit.PalEdit import PalInfo
from palworld_server_toolkit.PalEdit.PalEdit import PalEditConfig, PalEdit

pp = pprint.PrettyPrinter(width=80, compact=True, depth=4)
wsd = None
output_file = None
gvas_file = None
backup_gvas_file = None
backup_wsd = None
playerMapping = None
guildInstanceMapping = None
instanceMapping = None
output_path = None
args = None
player = None
filetime = -1
gui = None


def skip_decode(
        reader: FArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name == "ArrayProperty":
        array_type = reader.fstring()
        value = {
            "skip_type": type_name,
            "array_type": array_type,
            "id": reader.optional_guid(),
            "value": reader.read(size),
        }
    elif type_name == "MapProperty":
        key_type = reader.fstring()
        value_type = reader.fstring()
        _id = reader.optional_guid()
        value = {
            "skip_type": type_name,
            "key_type": key_type,
            "value_type": value_type,
            "id": _id,
            "value": reader.read(size),
        }
    elif type_name == "StructProperty":
        value = {
            "skip_type": type_name,
            "struct_type": reader.fstring(),
            "struct_id": reader.guid(),
            "id": reader.optional_guid(),
            "value": reader.read(size),
        }
    else:
        raise Exception(
            f"Expected ArrayProperty or MapProperty or StructProperty, got {type_name} in {path}"
        )
    return value


def skip_encode(
        writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type == "ArrayProperty":
        del properties["custom_type"]
        del properties["skip_type"]
        writer.fstring(properties["array_type"])
        writer.optional_guid(properties.get("id", None))
        writer.write(properties["value"])
        return len(properties["value"])
    elif property_type == "MapProperty":
        del properties["custom_type"]
        del properties["skip_type"]
        writer.fstring(properties["key_type"])
        writer.fstring(properties["value_type"])
        writer.optional_guid(properties.get("id", None))
        writer.write(properties["value"])
        return len(properties["value"])
    elif property_type == "StructProperty":
        del properties["custom_type"]
        del properties["skip_type"]
        writer.fstring(properties["struct_type"])
        writer.guid(properties["struct_id"])
        writer.optional_guid(properties.get("id", None))
        writer.write(properties["value"])
        return len(properties["value"])
    else:
        raise Exception(
            f"Expected ArrayProperty or MapProperty or StructProperty, got {property_type}"
        )


class skip_loading_progress(threading.Thread):
    def __init__(self, reader, size):
        super().__init__()
        self.reader = reader
        self.size = size

    def run(self) -> None:
        try:
            while not self.reader.eof():
                print("%3.0f%%" % (100 * self.reader.data.tell() / self.size), end="\b\b\b\b", flush=True)
                time.sleep(0.02)
        except ValueError:
            pass


def load_skiped_decode(wsd, skip_paths):
    if isinstance(skip_paths, str):
        skip_paths = [skip_paths]
    for skip_path in skip_paths:
        properties = wsd[skip_path]
        if "skip_type" not in properties:
            return

        print("Parsing worldSaveData.%s..." % skip_path, end="", flush=True)
        with FArchiveReader(
                properties['value'], PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES
        ) as reader:
            skip_loading_progress(reader, len(properties['value'])).start()
            if properties["skip_type"] == "ArrayProperty":
                properties['value'] = reader.array_property(properties["array_type"], len(properties['value']) - 4,
                                                            ".worldSaveData.%s" % skip_path)
            elif properties["skip_type"] == "StructProperty":
                properties['value'] = reader.struct_value(properties['struct_type'], ".worldSaveData.%s" % skip_path)
            elif properties["skip_type"] == "MapProperty":
                reader.u32()
                count = reader.u32()
                path = ".worldSaveData.%s" % skip_path
                key_path = path + ".Key"
                key_type = properties['key_type']
                value_type = properties['value_type']
                if key_type == "StructProperty":
                    key_struct_type = reader.get_type_or(key_path, "Guid")
                else:
                    key_struct_type = None
                value_path = path + ".Value"
                if value_type == "StructProperty":
                    value_struct_type = reader.get_type_or(value_path, "StructProperty")
                else:
                    value_struct_type = None
                values: list[dict[str, Any]] = []
                for _ in range(count):
                    key = reader.prop_value(key_type, key_struct_type, key_path)
                    value = reader.prop_value(value_type, value_struct_type, value_path)
                    values.append(
                        {
                            "key": key,
                            "value": value,
                        }
                    )
                properties["key_struct_type"] = key_struct_type
                properties["value_struct_type"] = value_struct_type
                properties["value"] = values
            del properties['custom_type']
            del properties["skip_type"]
        if ".worldSaveData.%s" % skip_path in SKP_PALWORLD_CUSTOM_PROPERTIES:
            del SKP_PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.%s" % skip_path]
        print("Done")


SKP_PALWORLD_CUSTOM_PROPERTIES = copy.deepcopy(PALWORLD_CUSTOM_PROPERTIES)
SKP_PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.MapObjectSaveData"] = (skip_decode, skip_encode)
SKP_PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.FoliageGridSaveDataMap"] = (skip_decode, skip_encode)
SKP_PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.MapObjectSpawnerInStageSaveData"] = (skip_decode, skip_encode)
SKP_PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.ItemContainerSaveData"] = (skip_decode, skip_encode)
SKP_PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.DynamicItemSaveData"] = (skip_decode, skip_encode)
SKP_PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.CharacterContainerSaveData"] = (skip_decode, skip_encode)
# SKP_PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.ItemContainerSaveData.Value"] = (skip_decode, skip_encode)

def main():
    global output_file, output_path, args, gui, playerMapping, instanceMapping

    parser = argparse.ArgumentParser(
        prog="palworld-save-editor",
        description="Editor for the Level.sav",
    )
    parser.add_argument("filename")
    parser.add_argument(
        "--fix-missing",
        action="store_true",
        help="Delete the missing characters",
    )
    parser.add_argument(
        "--statistics",
        action="store_true",
        help="Show the statistics for all key",
    )
    parser.add_argument(
        "--fix-capture",
        action="store_true",
        help="Fix the too many capture logs (not need after 1.4.0)",
    )
    parser.add_argument(
        "--fix-duplicate",
        action="store_true",
        help="Fix duplicate user data",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: <filename>_fixed.sav)",
    )
    parser.add_argument(
        "--gui",
        "-g",
        action="store_true",
        help="Open GUI",
    )

    if len(sys.argv) == 1:
        bk_f = filedialog.askopenfilename(filetypes=[("Level.sav file", "*.sav")], title="Open Level.sav")
        if bk_f:
            args = type('', (), {})()
            args.filename = bk_f
            args.gui = True
            args.statistics = False
            args.fix_missing = False
            args.fix_capture = False
            args.fix_duplicate = False
            args.output = None
        else:
            args = parser.parse_args()
    else:
        args = parser.parse_args()

    if not os.path.exists(args.filename):
        print(f"{args.filename} does not exist")
        exit(1)

    if not os.path.isfile(args.filename):
        print(f"{args.filename} is not a file")
        exit(1)

    LoadFile(args.filename)

    if args.statistics:
        Statistics()

    if args.output is None:
        output_path = args.filename.replace(".sav", "_fixed.sav")
    else:
        output_path = args.output

    ShowGuild()
    playerMapping, instanceMapping = LoadPlayers(data_source=wsd)
    ShowPlayers()

    if args.fix_missing:
        FixMissing()
    if args.fix_capture:
        FixCaptureLog()
    if args.fix_duplicate:
        FixDuplicateUser()

    if args.gui:
        GUI()

    if sys.flags.interactive:
        print("Go To Interactive Mode (no auto save), we have follow command:")
        print("  ShowPlayers()                              - List the Players")
        print("  FixMissing(dry_run=False)                  - Remove missing player instance")
        print("  FixCaptureLog(dry_run=False)               - Remove unused capture log")
        print("  FixDuplicateUser(dry_run=False)            - Remove duplicate player instance")
        print("  ShowGuild()                                - List the Guild and members")
        print("  BindGuildInstanceId(uid,instance_id)       - Update Guild binding instance for user")
        print("  RenamePlayer(uid,new_name)                 - Rename player to new_name")
        print("  DeletePlayer(uid,InstanceId=None,          ")
        print("               dry_run=False)                - Wipe player data from save")
        print("                                               InstanceId: delete specified InstanceId")
        print("                                               dry_run: only show how to delete")
        print("  EditPlayer(uid)                            - Allocate player base meta data to variable 'player'")
        print("  OpenBackup(filename)                       - Open Backup Level.sav file and assign to backup_wsd")
        print("  MigratePlayer(old_uid,new_uid)             - Migrate the player from old PlayerUId to new PlayerUId")
        print("                                               Note: the PlayerUId is use in the Sav file,")
        print("                                               when use to fix broken save, you can rename the old ")
        print("                                               player save to another UID and put in old_uid field.")
        print("  CopyPlayer(old_uid,new_uid, backup_wsd)    - Copy the player from old PlayerUId to new PlayerUId ")
        print("                                               Note: be sure you have already use the new playerUId to ")
        print("                                               login the game.")
        print("  Statistics()                               - Counting wsd block data size")
        print("  Save()                                     - Save the file and exit")
        print()
        print("Advance feature:")
        print("  search_key(wsd, '<value>')                 - Locate the key in the structure")
        print("  search_values(wsd, '<value>')              - Locate the value in the structure")
        print("  PrettyPrint(value)                         - Use XML format to show the value")
        return
    elif args.gui:
        gui.mainloop()
        return

    if args.fix_missing or args.fix_capture:
        Save()


class EntryPopup(tk.Entry):
    def __init__(self, parent, iid, column, **kw):
        ''' If relwidth is set, then width is ignored '''
        super().__init__(parent, **kw)
        self._textvariable = kw['textvariable']
        self.tv = parent
        self.iid = iid
        self.column = column
        global cc
        cc = self
        # self['state'] = 'readonly'
        # self['readonlybackground'] = 'white'
        # self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False
        self.focus_force()
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", lambda *ignore: self.destroy())

    def destroy(self) -> None:
        super().destroy()
        self.tv.set(self.iid, column=self.column, value=self._textvariable.get())

    def on_return(self, event):
        self.tv.item(self.iid, text=self.get())
        self.destroy()

    def select_all(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')
        # returns 'break' to interrupt default key-bindings
        return 'break'


class ParamEditor(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.gui = self
        self.parent = self
        #
        self.font = tk.font.Font(family="Courier New")

    def build_subgui(self, g_frame, attribute_key, attrib_var, attrib):
        sub_frame = ttk.Frame(master=g_frame)
        sub_frame.pack(side="right")
        sub_frame_c = ttk.Frame(master=sub_frame)
        cmbx = ttk.Combobox(master=sub_frame, font=self.font, width=20, state="readonly",
                            values=["Item %d" % i for i in range(len(attrib['value']['values']))])
        cmbx.bind("<<ComboboxSelected>>",
                  lambda evt: self.cmb_array_selected(evt, sub_frame_c, attribute_key, attrib_var, attrib))
        cmbx.pack(side="top")
        sub_frame_c.pack(side="top")

    def valid_int(self, value):
        try:
            int(value)
            return True
        except ValueError as e:
            return False

    def valid_float(self, value):
        try:
            float(value)
            return True
        except ValueError as e:
            return False

    @staticmethod
    def make_attrib_var(master, attrib):
        if not isinstance(attrib, dict):
            return None
        if attrib['type'] in ["IntProperty", "StrProperty", "NameProperty", "FloatProperty", "EnumProperty"]:
            return tk.StringVar(master)
        elif attrib['type'] == "StructProperty" and attrib['struct_type'] == "FixedPoint64" and \
                attrib['value']['Value']['type'] == "Int64Property":
            return tk.StringVar(master)
        elif attrib['type'] == "StructProperty" and attrib['struct_type'] == "Guid":
            return tk.StringVar(master)
        elif attrib['type'] == "BoolProperty":
            return tk.BooleanVar(master=master)
        elif attrib['type'] == "ArrayProperty" and attrib['array_type'] == "StructProperty":
            attrib_var = []
            for x in range(len(attrib['value']['values'])):
                attrib_var.append({})
            return attrib_var
        # elif attrib['type'] == "ArrayProperty" and attrib['array_type'] == "NameProperty":
        #     attrib_var = []
        #     return attrib_var

    def assign_attrib_var(self, var, attrib):
        if attrib['type'] in ["IntProperty", "StrProperty", "NameProperty", "FloatProperty"]:
            var.set(str(attrib['value']))
        elif attrib['type'] == "StructProperty" and attrib['struct_type'] == "FixedPoint64" and \
                attrib['value']['Value']['type'] == "Int64Property":
            var.set(str(attrib['value']['Value']['value']))
        elif attrib['type'] == "StructProperty" and attrib['struct_type'] == "Guid":
            var.set(str(attrib['value']))
        elif attrib['type'] == "BoolProperty":
            var.set(attrib['value'])
        elif attrib['type'] == "EnumProperty":
            var.set(attrib['value']['value'])

    def save(self, attribs, attrib_var, path=""):
        for attribute_key in attribs:
            attrib = attribs[attribute_key]
            if attribute_key not in attrib_var:
                continue
            if not isinstance(attrib, dict):
                continue
            if 'type' in attrib:
                if attrib['type'] == "IntProperty":
                    print("%s%s [%s] = %d -> %d" % (
                        path, attribute_key, attrib['type'], attribs[attribute_key]['value'],
                        int(attrib_var[attribute_key].get())))
                    attribs[attribute_key]['value'] = int(attrib_var[attribute_key].get())
                elif attrib['type'] == "FloatProperty":
                    print("%s%s [%s] = %f -> %f" % (
                        path, attribute_key, attrib['type'], attribs[attribute_key]['value'],
                        float(attrib_var[attribute_key].get())))
                    attribs[attribute_key]['value'] = float(attrib_var[attribute_key].get())
                elif attrib['type'] == "BoolProperty":
                    print(
                        "%s%s [%s] = %d -> %d" % (
                            path, attribute_key, attrib['type'], attribs[attribute_key]['value'],
                            attrib_var[attribute_key].get()))
                    attribs[attribute_key]['value'] = attrib_var[attribute_key].get()
                elif attrib['type'] == "StructProperty" and attrib['struct_type'] == "FixedPoint64":
                    if attrib['value']['Value']['type'] == "Int64Property":
                        print("%s%s [%s.%s] = %d -> %d" % (
                            path, attribute_key, attrib['type'], attrib['value']['Value']['type'],
                            attribs[attribute_key]['value']['Value']['value'],
                            int(attrib_var[attribute_key].get())))
                        attribs[attribute_key]['value']['Value']['value'] = int(attrib_var[attribute_key].get())
                    else:
                        print("Error: unsupported property type -> %s[%s.%s]" % (
                            attribute_key, attrib['type'], attrib['value']['Value']['type']))
                elif attrib['type'] == "StructProperty" and attrib['struct_type'] == "Guid":
                    print("%s%s [%s.%s] = %s -> %s" % (
                        path, attribute_key, attrib['type'], attrib['struct_type'],
                        str(attribs[attribute_key]['value']),
                        str(attrib_var[attribute_key].get())))
                    attribs[attribute_key]['value'] = to_storage_uuid(uuid.UUID(attrib_var[attribute_key].get()))
                elif attrib['type'] in ["StrProperty", "NameProperty"]:
                    print(
                        "%s%s [%s] = %s -> %s" % (
                            path, attribute_key, attrib['type'], attribs[attribute_key]['value'],
                            attrib_var[attribute_key].get()))
                    attribs[attribute_key]['value'] = attrib_var[attribute_key].get()
                elif attrib['type'] == "EnumProperty":
                    print(
                        "%s%s [%s - %s] = %s -> %s" % (path, attribute_key, attrib['type'], attrib['value']['type'],
                                                       attribs[attribute_key]['value']['value'],
                                                       attrib_var[attribute_key].get()))
                    attribs[attribute_key]['value']['value'] = attrib_var[attribute_key].get()
                elif attrib['type'] == "ArrayProperty" and attrib['array_type'] == "StructProperty":
                    for idx, item in enumerate(attrib['value']['values']):
                        print("%s%s [%s] = " % (path, attribute_key, attrib['type']))
                        self.save(item, attrib_var[attribute_key][idx], "%s[%d]." % (attribute_key, idx))
                elif attrib['type'] == "StructProperty":
                    if attrib_var[attribute_key] is None:
                        continue
                    for key in attrib['value']:
                        self.save({key: attrib['value'][key]}, attrib_var[attribute_key],
                                  "%s[\"%s\"]." % (attribute_key, key))
                else:
                    print("Error: unsupported property type -> %s[%s]" % (attribute_key, attrib['type']))

    def build_variable_gui(self, parent, attrib_var, attribs, with_labelframe=True):
        for attribute_key in attribs:
            attrib = attribs[attribute_key]
            if not isinstance(attrib, dict):
                continue
            if 'type' in attrib:
                if with_labelframe:
                    g_frame = tk.Frame(master=parent)
                    g_frame.pack(anchor=tk.constants.W, fill=tk.constants.X, expand=True)
                    tk.Label(master=g_frame, text=attribute_key, font=self.font).pack(side="left")
                else:
                    g_frame = parent

                attrib_var[attribute_key] = self.make_attrib_var(master=parent, attrib=attrib)
                if attrib['type'] == "BoolProperty":
                    tk.Checkbutton(master=g_frame, text="Enabled", variable=attrib_var[attribute_key]).pack(
                        side="left")
                    self.assign_attrib_var(attrib_var[attribute_key], attrib)
                elif attrib['type'] == "EnumProperty" and attrib['value']['type'] == "EPalWorkSuitability":
                    enum_options = ['EPalWorkSuitability::EmitFlame', 'EPalWorkSuitability::Watering',
                                    'EPalWorkSuitability::Seeding',
                                    'EPalWorkSuitability::GenerateElectricity', 'EPalWorkSuitability::Handcraft',
                                    'EPalWorkSuitability::Collection', 'EPalWorkSuitability::Deforest',
                                    'EPalWorkSuitability::Mining',
                                    'EPalWorkSuitability::OilExtraction', 'EPalWorkSuitability::ProductMedicine',
                                    'EPalWorkSuitability::Cool', 'EPalWorkSuitability::Transport',
                                    'EPalWorkSuitability::MonsterFarm']
                    if attrib['value']['value'] not in enum_options:
                        enum_options.append(attrib['value']['value'])
                    ttk.Combobox(master=g_frame, font=self.font, state="readonly",
                                 textvariable=attrib_var[attribute_key],
                                 values=enum_options).pack(side="right")
                    self.assign_attrib_var(attrib_var[attribute_key], attrib)
                elif attrib['type'] == "ArrayProperty" and attrib['array_type'] == "StructProperty":
                    self.build_subgui(g_frame, attribute_key, attrib_var[attribute_key], attrib)
                elif attrib['type'] == "StructProperty" and attrib['struct_type'] == "Guid":
                    tk.Entry(font=self.font, master=g_frame, width=50,
                             textvariable=attrib_var[attribute_key]).pack(
                        side="right", fill=tk.constants.X)
                    self.assign_attrib_var(attrib_var[attribute_key], attrib)
                elif attrib_var[attribute_key] is not None:
                    valid_cmd = None
                    if attrib['type'] in ["IntProperty"] or \
                            (attrib['type'] == "StructProperty" and attrib['struct_type'] == "FixedPoint64" and
                             attrib['value']['Value']['type'] == "Int64Property"):
                        valid_cmd = (self.register(self.valid_int), '%P')
                    elif attrib['type'] == "FloatProperty":
                        valid_cmd = (self.register(self.valid_float), '%P')

                    tk.Entry(font=self.font, master=g_frame,
                             validate='all', validatecommand=valid_cmd,
                             textvariable=attrib_var[attribute_key],
                             width=50).pack(
                        side="right", fill=tk.constants.X)
                    self.assign_attrib_var(attrib_var[attribute_key], attrib)
                elif attrib['type'] == "StructProperty":
                    attrib_var[attribute_key] = {}
                    sub_f = tk.Frame(master=g_frame)
                    sub_f.pack(side="right", fill=tk.constants.X)
                    for key in attrib['value']:
                        try:
                            attrib_var[attribute_key][key] = self.make_attrib_var(master=sub_f,
                                                                                  attrib=attrib['value'][key])
                            if attrib_var[attribute_key][key] is not None:
                                self.build_variable_gui(sub_f, attrib_var[attribute_key],
                                                        {key: attrib['value'][key]})
                        except TypeError as e:
                            print("Error attribute [%s]->%s " % (key, attribute_key), attrib)
                else:
                    print("  ", attribute_key, attrib['type'] + (
                        ".%s" % attrib['struct_type'] if attrib['type'] == "StructProperty" else ""), attrib['value'])
            else:
                print(attribute_key, attribs[attribute_key])
                continue

    def cmb_array_selected(self, evt, g_frame, attribute_key, attrib_var, attrib):
        for item in g_frame.winfo_children():
            item.destroy()
        print("Binding to %s[%d]" % (attribute_key, evt.widget.current()))
        self.build_variable_gui(g_frame, attrib_var[evt.widget.current()],
                                attrib['value']['values'][evt.widget.current()])

    @staticmethod
    def on_table_gui_dblclk(event, popup_set, columns, attrib_var):
        """ Executed, when a row is double-clicked. Opens 
        read-only EntryPopup above the item's column, so it is possible
        to select text """
        if popup_set.entryPopup is not None:
            popup_set.entryPopup.destroy()
            popup_set.entryPopup = None
        # what row and column was clicked on
        rowid = event.widget.identify_row(event.y)
        column = event.widget.identify_column(event.x)
        col_name = columns[int(column[1:]) - 1]
        # get column position info
        x, y, width, height = event.widget.bbox(rowid, column)
        # y-axis offset
        # pady = height // 2
        pady = height // 2
        popup_set.entryPopup = EntryPopup(event.widget, rowid, column, textvariable=attrib_var[int(rowid)][col_name])
        popup_set.entryPopup.place(x=x, y=y + pady, anchor=tk.constants.W, width=width)

    def build_array_gui_item(self, tables, idx, attrib_var, attrib_list):
        values = []
        for key in attrib_list:
            attrib = attrib_list[key]
            attrib_var[key] = self.make_attrib_var(tables, attrib)
            if attrib_var[key] is not None:
                self.assign_attrib_var(attrib_var[key], attrib)
                values.append(attrib_var[key].get())
        tables.insert(parent='', index='end', iid=idx, text='',
                      values=values)

    def build_array_gui(self, master, columns, attrib_var):
        popup_set = type('', (), {})()
        popup_set.entryPopup = None
        y_scroll = tk.Scrollbar(master)
        y_scroll.pack(side=tk.constants.RIGHT, fill=tk.constants.Y)
        x_scroll = tk.Scrollbar(master, orient='horizontal')
        x_scroll.pack(side=tk.constants.BOTTOM, fill=tk.constants.X)
        tables = ttk.Treeview(master, yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tables.pack(fill=tk.constants.BOTH)
        y_scroll.config(command=tables.yview)
        x_scroll.config(command=tables.xview)
        tables['columns'] = columns
        # format our column
        tables.column("#0", width=0, stretch=tk.constants.NO)
        for col in columns:
            tables.column(col, anchor=tk.constants.CENTER, width=10)
        # Create Headings
        tables.heading("#0", text="", anchor=tk.constants.CENTER)
        for col in columns:
            tables.heading(col, text=col, anchor=tk.constants.CENTER)
        tables.bind("<Double-1>", lambda event: self.on_table_gui_dblclk(event, popup_set, columns, attrib_var))
        return tables


class PlayerItemEdit(ParamEditor):
    def __init__(self, player_uid):
        load_skiped_decode(wsd, ['ItemContainerSaveData'])
        item_containers = {}
        for item_container in wsd["ItemContainerSaveData"]['value']:
            item_containers[str(item_container['key']['ID']['value'])] = item_container

        self.item_containers = {}
        self.item_container_vars = {}

        player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace(
            "-",
            "") + ".sav"
        if not os.path.exists(player_sav_file):
            messagebox.showerror("Player Itme Editor", "Player Sav file Not exists: %s" % player_sav_file)
            return
        else:
            with open(player_sav_file, "rb") as f:
                raw_gvas, _ = decompress_sav_to_gvas(f.read())
                player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
            player_gvas = player_gvas_file.properties['SaveData']['value']
        super().__init__()
        self.player_uid = player_uid
        self.player = \
            instanceMapping[str(playerMapping[player_uid]['InstanceId'])]['value']['RawData']['value']['object'][
                'SaveParameter']['value']
        self.gui.title("Player Item Edit - %s" % player_uid)
        tabs = ttk.Notebook(master=self)
        for idx_key in ['CommonContainerId', 'DropSlotContainerId', 'EssentialContainerId', 'FoodEquipContainerId',
                        'PlayerEquipArmorContainerId', 'WeaponLoadOutContainerId']:
            if str(player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value']) in item_containers:
                tab = tk.Frame(tabs)
                tabs.add(tab, text=idx_key[:-11])
                self.item_container_vars[idx_key[:-11]] = []
                item_container = item_containers[
                    str(player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value'])]
                self.item_containers[idx_key[:-11]] = [{
                    'SlotIndex': item['SlotIndex'],
                    'ItemId': item['ItemId']['value']['StaticId'],
                    'StackCount': item['StackCount']
                } for item in item_container['value']['Slots']['value']['values']]
                tables = self.build_array_gui(tab, ("SlotIndex", "ItemId", "StackCount"),
                                              self.item_container_vars[idx_key[:-11]])
                for idx, item in enumerate(self.item_containers[idx_key[:-11]]):
                    self.item_container_vars[idx_key[:-11]].append({})
                    self.build_array_gui_item(tables, idx, self.item_container_vars[idx_key[:-11]][idx], item)
        # 
        tabs.pack(side="top")
        tk.Button(master=self.gui, font=self.font, text="Save", command=self.savedata).pack(fill=tk.constants.X)

    def savedata(self):
        for idx_key in self.item_containers:
            for idx, item in enumerate(self.item_containers[idx_key]):
                self.save(self.item_containers[idx_key][idx], self.item_container_vars[idx_key][idx])
        self.destroy()


class PlayerSaveEdit(ParamEditor):
    def __init__(self, player_uid):
        self.player_sav_file = os.path.dirname(
            os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace(
            "-",
            "") + ".sav"
        if not os.path.exists(self.player_sav_file):
            messagebox.showerror("Player Itme Editor", "Player Sav file Not exists: %s" % self.player_sav_file)
            return
        else:
            with open(self.player_sav_file, "rb") as f:
                raw_gvas, _ = decompress_sav_to_gvas(f.read())
                self.player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
            player_gvas = self.player_gvas_file.properties['SaveData']['value']
        super().__init__()
        self.player_uid = player_uid
        self.player = player_gvas
        self.gui_attribute = {}
        self.gui.title("Player Save Edit - %s" % player_uid)
        self.build_variable_gui(self.gui, self.gui_attribute, self.player)
        tk.Button(master=self.gui, font=self.font, text="Save", command=self.savedata).pack(fill=tk.constants.X)

    def savedata(self):
        self.save(self.player, self.gui_attribute)
        with open(self.player_sav_file, "wb") as f:
            if "Pal.PalWorldSaveGame" in self.player_gvas_file.header.save_game_class_name or \
                    "Pal.PalLocalWorldSaveGame" in self.player_gvas_file.header.save_game_class_name:
                save_type = 0x32
            else:
                save_type = 0x31
            sav_file = compress_gvas_to_sav(self.player_gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type)
            f.write(sav_file)
        self.destroy()


class PlayerEditGUI(ParamEditor):
    def __init__(self, player_uid):
        super().__init__()
        self.player_uid = player_uid
        self.player = \
            instanceMapping[str(playerMapping[player_uid]['InstanceId'])]['value']['RawData']['value']['object'][
                'SaveParameter']['value']
        self.gui.title("Player Edit - %s" % player_uid)
        self.gui_attribute = {}
        self.build_variable_gui(self.gui, self.gui_attribute, self.player)
        tk.Button(master=self.gui, font=self.font, text="Save", command=self.savedata).pack(fill=tk.constants.X)

    def savedata(self):
        self.save(self.player, self.gui_attribute)
        self.destroy()

class PalEditGUI(PalEdit):
    def createWindow(self):
        root = tk.Toplevel()
        root.title(f"PalEdit v{PalEditConfig.version}")
        return root
    
    def load(self, file = None):
        paldata = wsd['CharacterSaveParameterMap']['value']
        
        nullmoves = []
        for i in paldata:
            try:
                p = PalInfo.PalEntity(i)
                if not str(p.owner) in self.palbox:
                    self.palbox[str(p.owner)] = []
                self.palbox[str(p.owner)].append(p)
                n = p.GetFullName()
                for m in p.GetLearntMoves():
                    if not m in nullmoves:
                        if not m in PalInfo.PalAttacks:
                            nullmoves.append(m)
            except Exception as e:
                if str(e) == "This is a player character":
                    print("Found Player Character")
                    # print(f"\nDebug: Data \n{i}\n\n")
                    o = i['value']['RawData']['value']['object']['SaveParameter']['value']
                    pl = "No Name"
                    if "NickName" in o:
                        pl = o['NickName']['value']
                    plguid = str(i['key']['PlayerUId']['value'])
                    print(f"{pl} - {plguid}")
                    self.players[pl] = plguid
                else:
                    self.unknown.append(i)
                    print(f"Error occured: {str(e)}")
                # print(f"Debug: Data {i}")
        
        print(self.palbox.keys())
        self.current.set(next(iter(self.players)))
        print(f"Defaulted selection to {self.current.get()}")
        self.updateDisplay()
        print(f"Unknown list contains {len(self.unknown)} entries")
        print(f"{len(self.players)} players found:")
        for i in self.players:
            print(f"{i} = {self.players[i]}")
        self.playerdrop['values'] = list(self.players.keys())
        self.playerdrop.current(0)
        nullmoves.sort()
        for i in nullmoves:
            print(f"{i} was not found in Attack Database")
            
        self.refresh()
        self.changetext(-1)
        self.jump()
        
    def build_menu(self):
        self.menu = tk.Menu(self.gui)
        tools = self.menu
        self.gui.config(menu=tools)
        toolmenu = tk.Menu(tools, tearoff=0)
        toolmenu.add_command(label="Debug", command=self.toggleDebug)
        toolmenu.add_command(label="Generate GUID", command=self.generateguid)
        tools.add_cascade(label="Tools", menu=toolmenu, underline=0)

class GUI():
    def __init__(self):
        global gui
        if gui is not None:
            gui.gui.destroy()
        gui = self
        self.gui = None
        self.src_player = None
        self.target_player = None
        self.data_source = None
        self.btn_migrate = None
        self.font = None
        self.build_gui()

    def mainloop(self):
        self.gui.mainloop()

    def gui_parse_uuid(self):
        src_uuid = self.src_player.get().split(" - ")[0]
        target_uuid = self.target_player.get().split(" - ")[0]
        if len(src_uuid) == 8:
            src_uuid += "-0000-0000-0000-000000000000"
        if len(target_uuid) == 8:
            target_uuid += "-0000-0000-0000-000000000000"
        try:
            uuid.UUID(src_uuid)
        except Exception as e:
            messagebox.showerror("Src Player Error", "UUID: \"%s\"\n%s" % (target_uuid, str(e)))
            return None, None

        try:
            uuid.UUID(target_uuid)
        except Exception as e:
            messagebox.showerror("Target Player Error", "UUID: \"%s\"\n%s" % (target_uuid, str(e)))
            return None, None

        return src_uuid, target_uuid

    def migrate(self):
        src_uuid, target_uuid = self.gui_parse_uuid()
        if src_uuid is None:
            return
        if src_uuid == target_uuid:
            messagebox.showerror("Error", "Src == Target ")
            return
        try:
            MigratePlayer(src_uuid, target_uuid)
            messagebox.showinfo("Result", "Migrate success")
            self.load_players()
        except Exception as e:
            messagebox.showerror("Migrate Error", str(e))

    def open_file(self):
        bk_f = filedialog.askopenfilename(filetypes=[("Level.sav file", "*.sav")], title="Open Level.sav")
        if bk_f:
            if self.data_source.current() == 0:
                LoadFile(bk_f)
            else:
                OpenBackup(bk_f)
            self.change_datasource(None)
            self.load_guilds()

    def copy_player(self):
        src_uuid, target_uuid = self.gui_parse_uuid()
        if src_uuid is None:
            return
        if src_uuid == target_uuid and self.data_source.current() == 0:
            messagebox.showerror("Error", "Src == Target ")
            return
        if self.data_source.current() == 1 and backup_wsd is None:
            messagebox.showerror("Error", "Backup file is not loaded")
            return
        try:
            CopyPlayer(src_uuid, target_uuid, wsd if self.data_source.current() == 0 else backup_wsd)
            messagebox.showinfo("Result", "Copy success")
            self.load_players()
        except Exception as e:
            messagebox.showerror("Copy Error", str(e))

    def load_players(self):
        _playerMapping, _ = LoadPlayers(wsd if self.data_source.current() == 0 else backup_wsd)
        src_value_lists = []
        for player_uid in _playerMapping:
            _player = _playerMapping[player_uid]
            try:
                _player['NickName'].encode('utf-8')
                src_value_lists.append(player_uid[0:8] + " - " + _player['NickName'])
            except UnicodeEncodeError:
                src_value_lists.append(player_uid[0:8] + " - *** ERROR ***")

        self.src_player.set("")
        self.src_player['value'] = src_value_lists

        _playerMapping, _ = LoadPlayers(wsd)
        target_value_lists = []
        for player_uid in _playerMapping:
            _player = _playerMapping[player_uid]
            try:
                _player['NickName'].encode('utf-8')
                target_value_lists.append(player_uid[0:8] + " - " + _player['NickName'])
            except UnicodeEncodeError:
                target_value_lists.append(player_uid[0:8] + " - *** ERROR ***")

        self.target_player['value'] = target_value_lists

    def load_guilds(self):
        guild_list = []
        for group_data in wsd['GroupSaveDataMap']['value']:
            if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
                group_info = group_data['value']['RawData']['value']
                guild_list.append("%s - %s" % (group_info['group_id'], group_info['guild_name']))
        self.target_guild['value'] = guild_list
        self.target_guild.set("")

    def change_datasource(self, x):
        if self.data_source.current() == 0:
            self.btn_migrate["state"] = "normal"
        else:
            self.btn_migrate["state"] = "disabled"
        self.load_players()

    def parse_target_uuid(self):
        target_uuid = self.target_player.get().split(" - ")[0]
        if len(target_uuid) == 8:
            target_uuid += "-0000-0000-0000-000000000000"
        try:
            uuid.UUID(target_uuid)
        except Exception as e:
            messagebox.showerror("Target Player Error", "UUID: \"%s\"\n%s" % (target_uuid, str(e)))
            return None
        if target_uuid not in playerMapping:
            messagebox.showerror("Target Player Not exists")
            return None
        return target_uuid

    def rename_player(self):
        target_uuid = self.parse_target_uuid()
        if target_uuid is None:
            return
        new_player_name = simpledialog.askstring(title="Rename Player", prompt="New player name",
                                                 initialvalue=playerMapping[target_uuid]['NickName'])
        if new_player_name:
            try:
                RenamePlayer(target_uuid, new_player_name)
                messagebox.showinfo("Result", "Rename success")
                self.load_players()
            except Exception as e:
                messagebox.showerror("Rename Error", str(e))

    def delete_player(self):
        target_uuid = self.parse_target_uuid()
        if target_uuid is None:
            return
        if 'yes' == messagebox.showwarning("Delete Player", "Confirm to delete player %s" % target_uuid,
                                           type=messagebox.YESNO):
            try:
                DeletePlayer(target_uuid)
                messagebox.showinfo("Result", "Delete success")
                self.load_players()
            except Exception as e:
                messagebox.showerror("Delete Error", str(e))

    def move_guild(self):
        target_uuid = self.parse_target_uuid()
        if target_uuid is None:
            return
        target_guild_uuid = self.target_guild.get().split(" - ")[0]
        try:
            uuid.UUID(target_guild_uuid)
        except Exception as e:
            messagebox.showerror("Target Guild Error", str(e))
            return None

        target_guild = None
        for group_data in wsd['GroupSaveDataMap']['value']:
            if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
                group_info = group_data['value']['RawData']['value']
                if group_info['group_id'] == target_guild_uuid:
                    target_guild = group_info
                    break
        if target_guild is None:
            messagebox.showerror("Target Guild is not found")
            return None
        try:
            MoveToGuild(target_uuid, target_guild_uuid)
            messagebox.showinfo("Result", "Move Guild success")
            self.load_players()
            self.load_guilds()
        except Exception as e:
            messagebox.showerror("Move Guild Error", str(e))

    def save(self):
        if 'yes' == messagebox.showwarning("Save", "Confirm to save file?", type=messagebox.YESNO):
            try:
                Save(False)
                messagebox.showinfo("Result", "Save to %s success" % output_path)
                print()
                sys.exit(0)
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def edit_player(self):
        target_uuid = self.parse_target_uuid()
        if target_uuid is None:
            return
        PlayerEditGUI(target_uuid)

    def edit_player_item(self):
        target_uuid = self.parse_target_uuid()
        if target_uuid is None:
            return
        PlayerItemEdit(target_uuid)

    def edit_player_save(self):
        target_uuid = self.parse_target_uuid()
        if target_uuid is None:
            return
        PlayerSaveEdit(target_uuid)
    
    def pal_edit(self):
        font_list = ('微软雅黑', 'Courier New', 'Arial')
        for font in font_list:
            if font in tkinter.font.families():
                PalEditConfig.font = font
                break
        pal = PalEditGUI()
        pal.load(None)
        pal.mainloop()

    def build_gui(self):
        #
        self.gui = tk.Tk()
        self.gui.parent = self
        try:
            __version__ = importlib.metadata.version('palworld-server-toolkit')
        except importlib.metadata.PackageNotFoundError:
            __version__ = "0.0.1"
        self.gui.title(f'PalWorld Save Editor v{__version__} - Author by MagicBear')
        # self.gui.geometry('640x200')
        #
        self.font = tk.font.Font(family="Courier New")
        self.gui.option_add('*TCombobox*Listbox.font', self.font)
        # window.resizable(False, False)
        f_src = tk.Frame()
        tk.Label(master=f_src, text="Data Source", font=self.font).pack(side="left")
        self.data_source = ttk.Combobox(master=f_src, font=self.font, width=20, values=['Main File', 'Backup File'],
                                        state="readonly")
        self.data_source.pack(side="left")
        self.data_source.current(0)
        self.data_source.bind("<<ComboboxSelected>>", self.change_datasource)
        g_open_file = tk.Button(master=f_src, font=self.font, text="Open File", command=self.open_file)
        g_open_file.pack(side="left")
        #
        f_src_player = tk.Frame()
        tk.Label(master=f_src_player, text="Source Player", font=self.font).pack(side="left")
        self.src_player = ttk.Combobox(master=f_src_player, font=self.font, width=50)
        self.src_player.pack(side="left")
        #
        f_target_player = tk.Frame()
        tk.Label(master=f_target_player, text="Target Player", font=self.font).pack(side="left")
        self.target_player = ttk.Combobox(master=f_target_player, font=self.font, width=50)
        self.target_player.pack(side="left")

        f_target_guild = tk.Frame()
        tk.Label(master=f_target_guild, text="Target Guild", font=self.font).pack(side="left")
        self.target_guild = ttk.Combobox(master=f_target_guild, font=self.font, width=80)
        self.target_guild.pack(side="left")
        #
        f_src.pack(anchor=tk.constants.W)
        f_src_player.pack(anchor=tk.constants.W)
        f_target_player.pack(anchor=tk.constants.W)
        f_target_guild.pack(anchor=tk.constants.W)
        g_button_frame = tk.Frame()
        self.btn_migrate = tk.Button(master=g_button_frame, text="Migrate Player", font=self.font, command=self.migrate)
        self.btn_migrate.pack(side="left")
        g_copy = tk.Button(master=g_button_frame, text="Copy Player", font=self.font, command=self.copy_player)
        g_copy.pack(side="left")
        g_pal = tk.Button(master=g_button_frame, text="Pal Edit", font=self.font, command=self.pal_edit)
        g_pal.pack(side="left")
        g_button_frame.pack()

        g_button_frame = tk.Frame()
        tk.Label(master=g_button_frame, text="Operate for Target Player", font=self.font).pack(fill="x", side="top")
        g_move = tk.Button(master=g_button_frame, text="Move To Guild", font=self.font, command=self.move_guild)
        g_move.pack(side="left")
        g_rename = tk.Button(master=g_button_frame, text="Rename", font=self.font, command=self.rename_player)
        g_rename.pack(side="left")
        g_delete = tk.Button(master=g_button_frame, text="Delete", font=self.font, command=self.delete_player)
        g_delete.pack(side="left")
        g_edit = tk.Button(master=g_button_frame, text="Edit", font=self.font, command=self.edit_player)
        g_edit.pack(side="left")
        g_edit_item = tk.Button(master=g_button_frame, text="Edit Item", font=self.font, command=self.edit_player_item)
        g_edit_item.pack(side="left")
        g_edit_save = tk.Button(master=g_button_frame, text="Edit Save", font=self.font, command=self.edit_player_save)
        g_edit_save.pack(side="left")
        g_button_frame.pack()

        g_save = tk.Button(text="Save & Exit", font=self.font, command=self.save)
        g_save.pack()

        self.load_players()
        self.load_guilds()


def LoadFile(filename):
    global filetime, gvas_file, wsd
    print(f"Loading {filename}...")
    filetime = os.stat(filename).st_mtime
    with open(filename, "rb") as f:
        # Read the file
        data = f.read()
        raw_gvas, _ = decompress_sav_to_gvas(data)

        print(f"Parsing {filename}...", end="", flush=True)
        start_time = time.time()
        gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, SKP_PALWORLD_CUSTOM_PROPERTIES)
        print("Done in %.1fs." % (time.time() - start_time))

    wsd = gvas_file.properties['worldSaveData']['value']


def Statistics():
    for key in wsd:
        print("%40s\t%.3f MB\tKey: %d" % (key, len(str(wsd[key])) / 1048576, len(wsd[key]['value'])))


def EditPlayer(player_uid):
    global player
    for item in wsd['CharacterSaveParameterMap']['value']:
        if str(item['key']['PlayerUId']['value']) == player_uid:
            player = item['value']['RawData']['value']['object']['SaveParameter']['value']
            print("Player has allocated to 'player' variable, you can use player['Property']['value'] = xxx to modify")
            pp.pprint(player)


def RenamePlayer(player_uid, new_name):
    for item in wsd['CharacterSaveParameterMap']['value']:
        if str(item['key']['PlayerUId']['value']) == player_uid:
            player = item['value']['RawData']['value']['object']['SaveParameter']['value']
            print(
                "\033[32mRename User\033[0m  UUID: %s  Level: %d  CharacterID: \033[93m%s\033[0m -> %s" % (
                    str(item['key']['InstanceId']['value']), player['Level']['value'],
                    player['NickName']['value'], new_name))
            player['NickName']['value'] = new_name
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for g_player in item['players']:
                if str(g_player['player_uid']) == player_uid:
                    print(
                        "\033[32mRename Guild User\033[0m  \033[93m%s\033[0m  -> %s" % (
                            g_player['player_info']['player_name'], new_name))
                    g_player['player_info']['player_name'] = new_name
                    break


def GetPlayerItems(player_uid):
    load_skiped_decode(wsd, ["ItemContainerSaveData"])
    item_containers = {}
    for item_container in wsd["ItemContainerSaveData"]['value']:
        item_containers[str(item_container['key']['ID']['value'])] = [{
            'ItemId': x['ItemId']['value']['StaticId']['value'],
            'SlotIndex': x['SlotIndex']['value'],
            'StackCount': x['StackCount']['value']
        }
            for x in item_container['value']['Slots']['value']['values']
        ]
    player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace("-",
                                                                                                                 "") + ".sav"
    if not os.path.exists(player_sav_file):
        print("\033[33mWarning: Player Sav file Not exists: %s\033[0m" % player_sav_file)
        return
    else:
        with open(player_sav_file, "rb") as f:
            raw_gvas, _ = decompress_sav_to_gvas(f.read())
            player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        player_gvas = player_gvas_file.properties['SaveData']['value']
        for idx_key in ['CommonContainerId', 'DropSlotContainerId', 'EssentialContainerId', 'FoodEquipContainerId',
                        'PlayerEquipArmorContainerId', 'WeaponLoadOutContainerId']:
            print("  %s" % player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value'])
            pp.pprint(item_containers[str(player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value'])])
            print()


def OpenBackup(filename):
    global backup_gvas_file, backup_wsd
    print(f"Loading {filename}...")
    with open(filename, "rb") as f:
        # Read the file
        data = f.read()
        raw_gvas, _ = decompress_sav_to_gvas(data)

        print(f"Parsing {filename}...", end="", flush=True)
        start_time = time.time()
        backup_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        print("Done in %.1fs." % (time.time() - start_time))
    backup_wsd = backup_gvas_file.properties['worldSaveData']['value']
    ShowPlayers(backup_wsd)


def to_storage_uuid(uuid_str):
    return UUID.from_str(str(uuid_str))


def CopyPlayer(player_uid, new_player_uid, old_wsd, dry_run=False):
    load_skiped_decode(wsd, ['ItemContainerSaveData', 'CharacterContainerSaveData'])
    player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace("-",
                                                                                                                 "") + ".sav"
    new_player_sav_file = os.path.dirname(
        os.path.abspath(args.filename)) + "/Players/" + new_player_uid.upper().replace("-", "") + ".sav"
    instances = []
    container_mapping = {}
    if not os.path.exists(player_sav_file):
        print("\033[33mWarning: Player Sav file Not exists: %s\033[0m" % player_sav_file)
        return
    else:
        with open(player_sav_file, "rb") as f:
            raw_gvas, _ = decompress_sav_to_gvas(f.read())
            player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        player_gvas = player_gvas_file.properties['SaveData']['value']
        player_uid = str(player_gvas['PlayerUId']['value'])
        player_gvas['PlayerUId']['value'] = to_storage_uuid(uuid.UUID(new_player_uid))
        player_gvas['IndividualId']['value']['PlayerUId']['value'] = player_gvas['PlayerUId']['value']
        player_gvas['IndividualId']['value']['InstanceId']['value'] = to_storage_uuid(uuid.uuid4())
    # Clone Item from CharacterContainerSaveData
    for idx_key in ['OtomoCharacterContainerId', 'PalStorageContainerId']:
        for container in old_wsd['CharacterContainerSaveData']['value']:
            if container['key']['ID']['value'] == player_gvas[idx_key]['value']['ID']['value']:
                new_item = copy.deepcopy(container)
                IsFound = False
                for idx, insert_item in enumerate(wsd['CharacterContainerSaveData']['value']):
                    if insert_item['key']['ID']['value'] == player_gvas[idx_key]['value']['ID']['value']:
                        player_gvas[idx_key]['value']['ID']['value'] = to_storage_uuid(uuid.uuid4())
                        new_item['key']['ID']['value'] = player_gvas[idx_key]['value']['ID']['value']
                        IsFound = True
                        break
                container_mapping[idx_key] = new_item
                if not dry_run:
                    wsd['CharacterContainerSaveData']['value'].append(new_item)
                if IsFound:
                    print(
                        "\033[32mCopy Character Container\033[0m %s UUID: %s -> %s" % (idx_key,
                                                                                       str(container['key']['ID'][
                                                                                               'value']), str(
                            new_item['key']['ID']['value'])))
                else:
                    print(
                        "\033[32mCopy Character Container\033[0m %s UUID: %s" % (idx_key,
                                                                                 str(container['key']['ID']['value'])))
                break
    for idx_key in ['CommonContainerId', 'DropSlotContainerId', 'EssentialContainerId', 'FoodEquipContainerId',
                    'PlayerEquipArmorContainerId', 'WeaponLoadOutContainerId']:
        for container in old_wsd['ItemContainerSaveData']['value']:
            if container['key']['ID']['value'] == player_gvas['inventoryInfo']['value'][idx_key]['value']['ID'][
                'value']:
                new_item = copy.deepcopy(container)
                IsFound = False
                for idx, insert_item in enumerate(wsd['ItemContainerSaveData']['value']):
                    if insert_item['key']['ID']['value'] == \
                            player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value']:
                        player_gvas['inventoryInfo']['value'][idx_key]['value']['ID']['value'] = to_storage_uuid(
                            uuid.uuid4())
                        new_item['key']['ID']['value'] = player_gvas['inventoryInfo']['value'][idx_key]['value']['ID'][
                            'value']
                        IsFound = True
                        break
                container_mapping[idx_key] = new_item
                if not dry_run:
                    wsd['ItemContainerSaveData']['value'].append(new_item)
                if IsFound:
                    print(
                        "\033[32mCopy Item Container\033[0m %s UUID: %s -> %s" % (idx_key,
                                                                                  str(container['key']['ID']['value']),
                                                                                  str(new_item['key']['ID']['value'])))
                else:
                    print(
                        "\033[32mCopy Item Container\033[0m %s UUID: %s" % (idx_key,
                                                                            str(container['key']['ID']['value'])))
                break
    IsFoundUser = None
    copy_user_params = None
    _playerMapping, _instanceMapping = LoadPlayers(wsd)

    for idx, insert_item in enumerate(wsd['CharacterSaveParameterMap']['value']):
        if str(insert_item['key']['PlayerUId']['value']) == new_player_uid:
            IsFoundUser = idx
            break
    for item in old_wsd['CharacterSaveParameterMap']['value']:
        player = item['value']['RawData']['value']['object']['SaveParameter']['value']
        if str(item['key']['PlayerUId']['value']) == player_uid and 'IsPlayer' in player and player['IsPlayer'][
            'value']:
            # if not IsFoundUser:
            copy_user_params = copy.deepcopy(item)
            copy_user_params['key']['PlayerUId']['value'] = to_storage_uuid(uuid.UUID(new_player_uid))
            copy_user_params['key']['InstanceId']['value'] = to_storage_uuid(
                uuid.UUID(str(player_gvas['IndividualId']['value']['InstanceId']['value'])))
            instances.append(
                {'guid': to_storage_uuid(uuid.UUID(new_player_uid)), 'instance_id': to_storage_uuid(
                    uuid.UUID(str(player_gvas['IndividualId']['value']['InstanceId']['value'])))})
        elif 'OwnerPlayerUId' in player and str(player['OwnerPlayerUId']['value']) == player_uid:
            IsFound = str(item['key']['InstanceId']['value']) in _instanceMapping
            new_item = copy.deepcopy(item)
            new_item['value']['RawData']['value']['object']['SaveParameter']['value']['OwnerPlayerUId']['value'] = \
                player_gvas['PlayerUId']['value']
            new_item['value']['RawData']['value']['object']['SaveParameter']['value']['SlotID']['value']['ContainerId'][
                'value']['ID'][
                'value'] = player_gvas['PalStorageContainerId']['value']['ID']['value']
            if IsFound:
                new_item['key']['InstanceId']['value'] = to_storage_uuid(uuid.uuid4())
                print(
                    "\033[32mCopy Pal\033[0m  UUID: %s -> %s  Owner: %s  CharacterID: %s" % (
                        str(item['key']['InstanceId']['value']), str(new_item['key']['InstanceId']['value']),
                        str(player['OwnerPlayerUId']['value']),
                        player['CharacterID']['value']))
            else:
                print(
                    "\033[32mCopy Pal\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                        str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                        player['CharacterID']['value']))
            if not dry_run:
                wsd['CharacterSaveParameterMap']['value'].append(new_item)
            instances.append(
                {'guid': player_gvas['PlayerUId']['value'], 'instance_id': new_item['key']['InstanceId']['value']})
    if IsFoundUser is None:
        if not dry_run:
            wsd['CharacterSaveParameterMap']['value'].append(copy_user_params)
        print("\033[32mCopy User\033[0m")
    else:
        wsd['CharacterSaveParameterMap']['value'][IsFoundUser] = copy_user_params
        print("\033[32mUpdate exists user to %s\033[0m" % copy_user_params['value']['RawData']['value']['object']
        ['SaveParameter']['value']['NickName']['value'])
    # Copy Item from GroupSaveDataMap
    player_group = None
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for g_player in item['players']:
                if str(g_player['player_uid']) == new_player_uid:
                    player_group = group_data
                    if not dry_run:
                        item['individual_character_handle_ids'] += instances
                    print(
                        "\033[32mCopy User \033[93m %s \033[0m -> \033[93m %s \033[32m to Guild\033[0m \033[32m %s \033[0m" % (
                            g_player['player_info']['player_name'],
                            copy_user_params['value']['RawData']['value']['object']['SaveParameter']['value'][
                                'NickName']['value'],
                            item['guild_name']))
                    copy_user_params['value']['RawData']['value']['group_id'] = group_data['value']['RawData']['value'][
                        'group_id']
                    break
    if player_group is None:
        for group_data in old_wsd['GroupSaveDataMap']['value']:
            if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
                item = group_data['value']['RawData']['value']
                for old_gplayer in item['players']:
                    if str(old_gplayer['player_uid']) == player_uid:
                        # Check group is exists
                        player_group = None
                        for chk_group_data in wsd['GroupSaveDataMap']['value']:
                            if str(group_data['key']) == str(chk_group_data['key']):
                                player_group = chk_group_data
                                break
                        # Same Guild is not exists in local save
                        if player_group is None:
                            print(
                                "\033[32mCopy Guild\033[0m  \033[93m%s\033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                                    g_player['player_info']['player_name'], str(g_player['player_uid']),
                                    g_player['player_info']['last_online_real_time']))
                            copy_user_params['value']['RawData']['value']['group_id'] = \
                                group_data['value']['RawData']['value']['group_id']
                            player_group = copy.deepcopy(group_data)
                            wsd['GroupSaveDataMap']['value'].append(player_group)
                            n_item = player_group['value']['RawData']['value']
                            for n_player_info in n_item['players']:
                                if str(n_player_info['player_uid']) == player_uid:
                                    n_player_info['player_uid'] = to_storage_uuid(uuid.UUID(new_player_uid))
                                    n_item['players'] = [n_player_info]
                                    break
                            n_item['individual_character_handle_ids'] = instances
                        else:
                            # Same Guild already has a group on local
                            group_info = group_data['value']['RawData']['value']
                            print(
                                "\033[32mGuild \033[93m %s \033[0m exists\033[0m  Group ID \033[92m %s \033[0m   " % (
                                    group_info['guild_name'], group_info['group_id']))
                            copy_user_params['value']['RawData']['value']['group_id'] = group_info['group_id']
                            n_item = player_group['value']['RawData']['value']
                            is_player_found = False
                            for n_player_info in n_item['players']:
                                if str(n_player_info['player_uid']) == new_player_uid:
                                    n_player_info['player_info'] = copy.deepcopy(n_player_info['player_info'])
                                    is_player_found = True
                                    break
                            if not is_player_found:
                                print("\033[32mAdd User to Guild\033[0m  \033[93m%s\033[0m" % (
                                    copy_user_params['value']['RawData']['value']['object']['SaveParameter']['value'][
                                        'NickName']['value']))
                                n_item['players'].append({
                                    'player_uid': to_storage_uuid(uuid.UUID(new_player_uid)),
                                    'player_info': {
                                        'last_online_real_time': 0,
                                        'player_name':
                                            copy_user_params['value']['RawData']['value']['object']['SaveParameter'][
                                                'value']['NickName']['value']
                                    }
                                })
                            n_item['individual_character_handle_ids'] = instances
                        break
                if not dry_run:
                    item['individual_character_handle_ids'] += instances
    if not dry_run:
        with open(new_player_sav_file, "wb") as f:
            print("Saving new player sav %s" % (new_player_sav_file))
            if "Pal.PalWorldSaveGame" in player_gvas_file.header.save_game_class_name or "Pal.PalLocalWorldSaveGame" in player_gvas_file.header.save_game_class_name:
                save_type = 0x32
            else:
                save_type = 0x31
            sav_file = compress_gvas_to_sav(player_gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type)
            f.write(sav_file)


def MoveToGuild(player_uid, group_id):
    target_group = None
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            group_info = group_data['value']['RawData']['value']
            if group_info['group_id'] == group_id:
                target_group = group_info
    if target_group is None:
        print("\033[31mError: cannot found target guild")
        return

    instances = []
    remove_instance_ids = []
    playerInstance = None

    for item in wsd['CharacterSaveParameterMap']['value']:
        player = item['value']['RawData']['value']['object']['SaveParameter']['value']
        if str(item['key']['PlayerUId']['value']) == player_uid and 'IsPlayer' in player and player['IsPlayer'][
            'value']:
            playerInstance = player
            instances.append({
                'guid': item['key']['PlayerUId']['value'],
                'instance_id': item['key']['InstanceId']['value']
            })
            remove_instance_ids.append(item['key']['InstanceId']['value'])
        elif 'OwnerPlayerUId' in player and str(player['OwnerPlayerUId']['value']) == player_uid:
            instances.append({
                'guid': to_storage_uuid(uuid.UUID("00000000-0000-0000-0000-000000000000")),
                'instance_id': item['key']['InstanceId']['value']
            })
            remove_instance_ids.append(item['key']['InstanceId']['value'])

    remove_guilds = []
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            group_info = group_data['value']['RawData']['value']
            delete_g_players = []
            for g_player in group_info['players']:
                if str(g_player['player_uid']) == player_uid:
                    delete_g_players.append(g_player)
                    print(
                        "\033[31mDelete player \033[93m %s \033[31m on guild \033[93m %s \033[0m [\033[92m %s \033[0m] " % (
                            g_player['player_info']['player_name'], group_info['guild_name'], group_info['group_id']))

            for g_player in delete_g_players:
                group_info['players'].remove(g_player)

            if len(group_info['players']) == 0:
                remove_guilds.append(group_data)
                print("\033[31mDelete Guild\033[0m \033[93m %s \033[0m  UUID: %s" % (
                    group_info['guild_name'], str(group_info['group_id'])))

            remove_items = []
            for ind_id in group_info['individual_character_handle_ids']:
                if ind_id['instance_id'] in remove_instance_ids:
                    remove_items.append(ind_id)
                    print(
                        "\033[31mDelete guild [\033[92m %s \033[31m] character handle GUID \033[92m %s \033[0m [InstanceID \033[92m %s \033[0m] " % (
                            group_info['group_id'], ind_id['guid'], ind_id['instance_id']))
            for item in remove_items:
                group_info['individual_character_handle_ids'].remove(item)

    for guild in remove_guilds:
        wsd['GroupSaveDataMap']['value'].remove(guild)

    print("\033[32mAppend character and players to guild\033[0m")
    target_group['players'].append({
        'player_uid': to_storage_uuid(uuid.UUID(player_uid)),
        'player_info': {
            'last_online_real_time': 0,
            'player_name':
                playerInstance['NickName']['value']
        }
    })
    target_group['individual_character_handle_ids'] += instances


def MigratePlayer(player_uid, new_player_uid):
    load_skiped_decode(wsd, ['MapObjectSaveData'])

    player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace("-",
                                                                                                                 "") + ".sav"
    new_player_sav_file = os.path.dirname(
        os.path.abspath(args.filename)) + "/Players/" + new_player_uid.upper().replace("-", "") + ".sav"
    DeletePlayer(new_player_uid)
    if not os.path.exists(player_sav_file):
        print("\033[33mWarning: Player Sav file Not exists: %s\033[0m" % player_sav_file)
        return
    else:
        with open(player_sav_file, "rb") as f:
            raw_gvas, _ = decompress_sav_to_gvas(f.read())
            player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        player_gvas = player_gvas_file.properties['SaveData']['value']
        player_uid = player_gvas['PlayerUId']['value']
        player_gvas['PlayerUId']['value'] = to_storage_uuid(uuid.UUID(new_player_uid))
        player_gvas['IndividualId']['value']['PlayerUId']['value'] = player_gvas['PlayerUId']['value']
        player_gvas['IndividualId']['value']['InstanceId']['value'] = to_storage_uuid(uuid.uuid4())
        with open(new_player_sav_file, "wb") as f:
            print("Saving new player sav %s" % new_player_sav_file)
            if "Pal.PalWorldSaveGame" in player_gvas_file.header.save_game_class_name or "Pal.PalLocalWorldSaveGame" in player_gvas_file.header.save_game_class_name:
                save_type = 0x32
            else:
                save_type = 0x31
            sav_file = compress_gvas_to_sav(player_gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type)
            f.write(sav_file)
    for item in wsd['CharacterSaveParameterMap']['value']:
        player = item['value']['RawData']['value']['object']['SaveParameter']['value']
        if str(item['key']['PlayerUId']['value']) == str(player_uid) and \
                'IsPlayer' in player and player['IsPlayer']['value']:
            item['key']['PlayerUId']['value'] = player_gvas['PlayerUId']['value']
            item['key']['InstanceId']['value'] = player_gvas['IndividualId']['value']['InstanceId']['value']
            print(
                "\033[32mMigrate User\033[0m  UUID: %s  Level: %d  CharacterID: \033[93m%s\033[0m" % (
                    str(item['key']['InstanceId']['value']), player['Level']['value'] if 'Level' in player else -1,
                    player['NickName']['value']))
        elif 'OwnerPlayerUId' in player and str(player['OwnerPlayerUId']['value']) == str(player_uid):
            player['OwnerPlayerUId']['value'] = to_storage_uuid(uuid.UUID(new_player_uid))
            player['OldOwnerPlayerUIds']['value']['values'].insert(0, to_storage_uuid(uuid.UUID(new_player_uid)))
            print(
                "\033[32mMigrate Pal\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                    str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                    player['CharacterID']['value']))
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for player in item['players']:
                if str(player['player_uid']) == str(player_uid):
                    player['player_uid'] = player_gvas['PlayerUId']['value']
                    print(
                        "\033[32mMigrate User from Guild\033[0m  \033[93m%s\033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                            player['player_info']['player_name'], str(player['player_uid']),
                            player['player_info']['last_online_real_time']))
                    remove_handle_ids = []
                    for ind_char in item['individual_character_handle_ids']:
                        if str(ind_char['guid']) == str(player_uid):
                            remove_handle_ids.append(ind_char)
                            print("\033[31mDelete Guild Character InstanceID %s \033[0m" % str(ind_char['instance_id']))
                    for remove_handle in remove_handle_ids:
                        item['individual_character_handle_ids'].remove(remove_handle)
                    item['individual_character_handle_ids'].append({
                        'guid': player_gvas['PlayerUId']['value'],
                        'instance_id': player_gvas['IndividualId']['value']['InstanceId']['value']
                    })
                    print("\033[32mAppend Guild Character InstanceID %s \033[0m" % (
                        str(player_gvas['IndividualId']['value']['InstanceId']['value'])))
                    break
            if str(item['admin_player_uid']) == str(player_uid):
                item['admin_player_uid'] = player_gvas['PlayerUId']['value']
                print("\033[32mMigrate Guild Admin \033[0m")
    for map_data in wsd['MapObjectSaveData']['value']['values']:
        if str(map_data['Model']['value']['RawData']['value']['build_player_uid']) == str(player_uid):
            map_data['Model']['value']['RawData']['value']['build_player_uid'] = player_gvas['PlayerUId']['value']
            print(
                "\033[32mMigrate Building\033[0m  \033[93m%s\033[0m" % (
                    str(map_data['MapObjectInstanceId']['value'])))
    print("Finish to migrate player from Save, please delete this file manually: %s" % player_sav_file)


def DeletePlayer(player_uid, InstanceId=None, dry_run=False):
    load_skiped_decode(wsd, ['ItemContainerSaveData', 'CharacterContainerSaveData'])
    if isinstance(player_uid, int):
        player_uid = str(uuid.UUID("%08x-0000-0000-0000-000000000000" % player_uid))
    player_sav_file = os.path.dirname(os.path.abspath(args.filename)) + "/Players/" + player_uid.upper().replace("-",
                                                                                                                 "") + ".sav"
    player_container_ids = []
    playerInstanceId = None
    if InstanceId is None:
        if not os.path.exists(player_sav_file):
            print("\033[33mWarning: Player Sav file Not exists: %s\033[0m" % player_sav_file)
            player_gvas_file = None
        else:
            with open(player_sav_file, "rb") as f:
                raw_gvas, _ = decompress_sav_to_gvas(f.read())
                player_gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
            print("Player Container ID:")
            player_gvas = player_gvas_file.properties['SaveData']['value']
            playerInstanceId = player_gvas['IndividualId']['value']['InstanceId']['value']
            for key in ['OtomoCharacterContainerId', 'PalStorageContainerId']:
                print("  %s" % player_gvas[key]['value']['ID']['value'])
                player_container_ids.append(player_gvas[key]['value']['ID']['value'])
            for key in ['CommonContainerId', 'DropSlotContainerId', 'EssentialContainerId', 'FoodEquipContainerId',
                        'PlayerEquipArmorContainerId', 'WeaponLoadOutContainerId']:
                print("  %s" % player_gvas['inventoryInfo']['value'][key]['value']['ID']['value'])
                player_container_ids.append(player_gvas['inventoryInfo']['value'][key]['value']['ID']['value'])
    else:
        playerInstanceId = InstanceId
    remove_items = []
    remove_instance_id = []
    # Remove item from CharacterSaveParameterMap
    for item in wsd['CharacterSaveParameterMap']['value']:
        player = item['value']['RawData']['value']['object']['SaveParameter']['value']
        if str(item['key']['PlayerUId']['value']) == player_uid \
                and 'IsPlayer' in player and player['IsPlayer']['value'] \
                and (InstanceId is None or str(item['key']['InstanceId']['value']) == InstanceId):
            remove_items.append(item)
            remove_instance_id.append(item['key']['InstanceId']['value'])
            print(
                "\033[31mDelete User\033[0m  UUID: %s  Level: %d  CharacterID: \033[93m%s\033[0m" % (
                    str(item['key']['InstanceId']['value']), player['Level']['value'] if 'Level' in player else -1,
                    player['NickName']['value']))
        elif 'OwnerPlayerUId' in player and str(player['OwnerPlayerUId']['value']) == player_uid and InstanceId is None:
            remove_instance_id.append(item['key']['InstanceId']['value'])
            print(
                "\033[31mDelete Pal\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                    str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                    player['CharacterID']['value']))
            remove_items.append(item)
        elif 'SlotID' in player and player['SlotID']['value']['ContainerId']['value']['ID'][
            'value'] in player_container_ids and InstanceId is None:
            remove_instance_id.append(item['key']['InstanceId']['value'])
            print(
                "\033[31mDelete Pal\033[0m  UUID: %s  Slot: %s  CharacterID: %s" % (
                    str(item['key']['InstanceId']['value']),
                    str(player['SlotID']['value']['ContainerId']['value']['ID']['value']),
                    player['CharacterID']['value']))
            remove_items.append(item)
    if not dry_run:
        for item in remove_items:
            wsd['CharacterSaveParameterMap']['value'].remove(item)
    # Remove Item from CharacterContainerSaveData
    remove_items = []
    for container in wsd['CharacterContainerSaveData']['value']:
        if container['key']['ID']['value'] in player_container_ids:
            remove_items.append(container)
            print(
                "\033[31mDelete Character Container\033[0m  UUID: %s" % (
                    str(container['key']['ID']['value'])))
    if not dry_run:
        for item in remove_items:
            wsd['CharacterContainerSaveData']['value'].remove(item)
    # Remove Item from ItemContainerSaveData
    remove_items = []
    for container in wsd['ItemContainerSaveData']['value']:
        if container['key']['ID']['value'] in player_container_ids:
            remove_items.append(container)
            print(
                "\033[31mDelete Item Container\033[0m  UUID: %s" % (
                    str(container['key']['ID']['value'])))
    if not dry_run:
        for item in remove_items:
            wsd['ItemContainerSaveData']['value'].remove(item)
    # Remove Item from CharacterSaveParameterMap
    remove_items = []
    for container in wsd['CharacterSaveParameterMap']['value']:
        if container['key']['InstanceId']['value'] == playerInstanceId:
            remove_items.append(container)
            print(
                "\033[31mDelete CharacterSaveParameterMap\033[0m  UUID: %s" % (
                    str(container['key']['InstanceId']['value'])))
    if not dry_run:
        for item in remove_items:
            wsd['CharacterSaveParameterMap']['value'].remove(item)
    # Remove Item from GroupSaveDataMap
    remove_guilds = []
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for player in item['players']:
                if str(player['player_uid']) == player_uid and InstanceId is None:
                    print(
                        "\033[31mDelete User \033[93m %s \033[0m from Guild\033[0m \033[93m %s \033[0m   [\033[92m%s\033[0m] Last Online: %d" % (
                            player['player_info']['player_name'],
                            item['guild_name'], str(player['player_uid']),
                            player['player_info']['last_online_real_time']))
                    if not dry_run:
                        item['players'].remove(player)
                        if len(item['players']) == 0:
                            remove_guilds.append(group_data)
                            print("\033[31mDelete Guild\033[0m \033[93m %s \033[0m  UUID: %s" % (
                                item['guild_name'], str(item['group_id'])))
                    break
            removeItems = []
            for ind_char in item['individual_character_handle_ids']:
                if ind_char['instance_id'] in remove_instance_id:
                    print("\033[31mDelete Guild Character %s\033[0m" % (str(ind_char['instance_id'])))
                    removeItems.append(ind_char)
            if not dry_run:
                for ind_char in removeItems:
                    item['individual_character_handle_ids'].remove(ind_char)
    for guild in remove_guilds:
        wsd['GroupSaveDataMap']['value'].remove(guild)
    if InstanceId is None:
        print("Finish to remove player from Save, please delete this file manually: %s" % player_sav_file)


def search_keys(dicts, key, level=""):
    if isinstance(dicts, dict):
        if key in dicts:
            print("Found at %s->%s" % (level, key))
        for k in dicts:
            if isinstance(dicts[k], dict) or isinstance(dicts[k], list):
                search_keys(dicts[k], key, level + "->" + k)
    elif isinstance(dicts, list):
        for idx, l in enumerate(dicts):
            if isinstance(l, dict) or isinstance(l, list):
                search_keys(l, key, level + "[%d]" % idx)


def search_values(dicts, key, level=""):
    try:
        uuid_match = uuid.UUID(str(key))
    except ValueError:
        uuid_match = None
    isFound = False
    if isinstance(dicts, dict):
        if key in dicts.values():
            print("Found value at %s['%s']" % (level, list(dicts.keys())[list(dicts.values()).index(key)]))
            isFound = True
        elif uuid_match is not None and uuid_match in dicts.values():
            print("Found UUID  at %s['%s']" % (level, list(dicts.keys())[list(dicts.values()).index(uuid_match)]))
            isFound = True
        for k in dicts:
            if level == "":
                print("Searching %s" % k)
            if isinstance(dicts[k], dict) or isinstance(dicts[k], list):
                isFound |= search_values(dicts[k], key, level + "['%s']" % k)
    elif isinstance(dicts, list):
        if key in dicts:
            print("Found value at %s[%d]" % (level, dicts.index(key)))
            isFound = True
        elif uuid_match is not None and uuid_match in dicts:
            print("Found UUID  at %s[%d]" % (level, dicts.index(uuid_match)))
            isFound = True
        for idx, l in enumerate(dicts):
            if level == "":
                print("Searching %s" % l)
            if isinstance(l, dict) or isinstance(l, list):
                isFound |= search_values(l, key, level + "[%d]" % idx)
    return isFound


def LoadPlayers(data_source=None):
    global wsd, playerMapping, instanceMapping
    if data_source is None:
        data_source = wsd

    l_playerMapping = {}
    l_instanceMapping = {}
    for item in data_source['CharacterSaveParameterMap']['value']:
        l_instanceMapping[str(item['key']['InstanceId']['value'])] = item
        playerStruct = item['value']['RawData']['value']['object']['SaveParameter']
        playerParams = playerStruct['value']
        # if "00000000-0000-0000-0000-000000000000" != str(item['key']['PlayerUId']['value']):
        if 'IsPlayer' in playerParams and playerParams['IsPlayer']['value']:
            if playerStruct['struct_type'] == 'PalIndividualCharacterSaveParameter':
                if 'OwnerPlayerUId' in playerParams:
                    print(
                        "\033[33mWarning: Corrupted player struct\033[0m UUID \033[32m %s \033[0m Owner \033[32m %s \033[0m" % (
                            str(item['key']['PlayerUId']['value']), str(playerParams['OwnerPlayerUId']['value'])))
                    pp.pprint(playerParams)
                    playerParams['IsPlayer']['value'] = False
                elif 'NickName' in playerParams:
                    try:
                        playerParams['NickName']['value'].encode('utf-8')
                    except UnicodeEncodeError as e:
                        print("\033[33mWarning: Corrupted player name\033[0m UUID \033[32m %s \033[0m Player \033[32m %s \033[0m" % (
                            str(item['key']['PlayerUId']['value']), repr(playerParams['NickName']['value'])))
                playerMeta = {}
                for player_k in playerParams:
                    playerMeta[player_k] = playerParams[player_k]['value']
                playerMeta['InstanceId'] = item['key']['InstanceId']['value']
                l_playerMapping[str(item['key']['PlayerUId']['value'])] = playerMeta
    if data_source == wsd:
        playerMapping = l_playerMapping
        instanceMapping = l_instanceMapping
    return l_playerMapping, l_instanceMapping


def ShowPlayers(data_source=None):
    global guildInstanceMapping
    playerMapping, _ = LoadPlayers(data_source)
    for playerUId in playerMapping:
        playerMeta = playerMapping[playerUId]
        try:
            print("PlayerUId \033[32m %s \033[0m [InstanceID %s %s \033[0m] -> Level %2d  %s" % (
                playerUId,
                "\033[33m" if str(playerUId) in guildInstanceMapping and
                              str(playerMeta['InstanceId']) == guildInstanceMapping[
                                  str(playerUId)] else "\033[31m", playerMeta['InstanceId'],
                playerMeta['Level'] if 'Level' in playerMeta else -1, playerMeta['NickName']))
        except UnicodeEncodeError as e:
            print("Corrupted Player Name \033[31m %s \033[0m PlayerUId \033[32m %s \033[0m [InstanceID %s %s \033[0m]" %
                  (repr(playerMeta['NickName']), playerUId, "\033[33m" if str(playerUId) in guildInstanceMapping and
                              str(playerMeta['InstanceId']) == guildInstanceMapping[
                                  str(playerUId)] else "\033[31m", playerMeta['InstanceId']))
        except KeyError:
            print("PlayerUId \033[32m %s \033[0m [InstanceID %s %s \033[0m] -> Level %2d" % (
                playerUId,
                "\033[33m" if str(playerUId) in guildInstanceMapping and
                              str(playerMeta['InstanceId']) == guildInstanceMapping[
                                  str(playerUId)] else "\033[31m", playerMeta['InstanceId'],
                playerMeta['Level'] if 'Level' in playerMeta else -1))


def FixMissing(dry_run=False):
    # Remove Unused in CharacterSaveParameterMap
    removeItems = []
    for item in wsd['CharacterSaveParameterMap']['value']:
        if "00000000-0000-0000-0000-000000000000" == str(item['key']['PlayerUId']['value']):
            player = item['value']['RawData']['value']['object']['SaveParameter']['value']
            if 'OwnerPlayerUId' in player and str(player['OwnerPlayerUId']['value']) not in playerMapping:
                print(
                    "\033[31mInvalid item on CharacterSaveParameterMap\033[0m  UUID: %s  Owner: %s  CharacterID: %s" % (
                        str(item['key']['InstanceId']['value']), str(player['OwnerPlayerUId']['value']),
                        player['CharacterID']['value']))
                removeItems.append(item)
    if not dry_run:
        for item in removeItems:
            wsd['CharacterSaveParameterMap']['value'].remove(item)


def FixCaptureLog(dry_run=False):
    global instanceMapping

    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            removeItems = []
            for ind_char in item['individual_character_handle_ids']:
                if str(ind_char['instance_id']) not in instanceMapping:
                    print("    \033[31mInvalid Character %s\033[0m" % (str(ind_char['instance_id'])))
                    removeItems.append(ind_char)
            print("After remove character count: %d" % (len(
                group_data['value']['RawData']['value']['individual_character_handle_ids']) - len(removeItems)))
            if dry_run:
                for rm_item in removeItems:
                    item['individual_character_handle_ids'].remove(rm_item)


def FixDuplicateUser(dry_run=False):
    # Remove Unused in CharacterSaveParameterMap
    removeItems = []
    for item in wsd['CharacterSaveParameterMap']['value']:
        if "00000000-0000-0000-0000-000000000000" != str(item['key']['PlayerUId']['value']):
            player_meta = item['value']['RawData']['value']['object']['SaveParameter']['value']
            if str(item['key']['PlayerUId']['value']) not in guildInstanceMapping:
                print(
                    "\033[31mInvalid player on CharacterSaveParameterMap\033[0m  PlayerUId: %s  InstanceID: %s  Nick: %s" % (
                        str(item['key']['PlayerUId']['value']), str(item['key']['InstanceId']['value']),
                        str(player_meta['NickName']['value'])))
                removeItems.append(item)
            elif str(item['key']['InstanceId']['value']) != guildInstanceMapping[
                str(item['key']['PlayerUId']['value'])]:
                print(
                    "\033[31mDuplicate player on CharacterSaveParameterMap\033[0m  PlayerUId: %s  InstanceID: %s  Nick: %s" % (
                        str(item['key']['PlayerUId']['value']), str(item['key']['InstanceId']['value']),
                        str(player_meta['NickName']['value'])))
                removeItems.append(item)
    if not dry_run:
        for item in removeItems:
            wsd['CharacterSaveParameterMap']['value'].remove(item)


def TickToHuman(tick):
    seconds = (wsd['GameTimeSaveData']['value']['RealDateTimeTicks']['value'] - tick) / 1e7
    s = ""
    if seconds > 86400:
        s += " %d d" % (seconds // 86400)
        seconds %= 86400
    if seconds > 3600:
        s += " %d h" % (seconds // 3600)
        seconds %= 3600
    if seconds > 60:
        s += " %d m" % (seconds // 60)
        seconds %= 60
    s += " %d s" % seconds
    return s


def TickToLocal(tick):
    ts = filetime + (tick - wsd['GameTimeSaveData']['value']['RealDateTimeTicks']['value']) / 1e7
    t = datetime.datetime.fromtimestamp(ts)
    return t.strftime("%Y-%m-%d %H:%M:%S")


def BindGuildInstanceId(uid, instance_id):
    for group_data in wsd['GroupSaveDataMap']['value']:
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            item = group_data['value']['RawData']['value']
            for ind_char in item['individual_character_handle_ids']:
                if str(ind_char['guid']) == uid:
                    print("Update Guild %s binding guild UID %s  %s -> %s" % (
                        item['guild_name'], uid, ind_char['instance_id'], instance_id))
                    ind_char['instance_id'] = to_storage_uuid(uuid.UUID(instance_id))
                    guildInstanceMapping[str(ind_char['guid'])] = str(ind_char['instance_id'])
            print()


def ShowGuild():
    global guildInstanceMapping
    guildInstanceMapping = {}
    # Remove Unused in GroupSaveDataMap
    for group_data in wsd['GroupSaveDataMap']['value']:
        # print("%s %s" % (group_data['key'], group_data['value']['GroupType']['value']['value']))
        if str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Guild":
            # pp.pprint(str(group_data['value']['RawData']['value']))
            item = group_data['value']['RawData']['value']
            mapObjectMeta = {}
            for m_k in item:
                mapObjectMeta[m_k] = item[m_k]
            # pp.pprint(mapObjectMeta)
            print("Guild \033[93m%s\033[0m   Admin \033[96m%s\033[0m  Group ID %s  Character Count: %d" % (
                mapObjectMeta['guild_name'], str(mapObjectMeta['admin_player_uid']), str(mapObjectMeta['group_id']),
                len(mapObjectMeta['individual_character_handle_ids'])))
            for player in mapObjectMeta['players']:
                try:
                    print("    Player \033[93m %-30s \033[0m\t[\033[92m%s\033[0m] Last Online: %s - %s" % (
                        player['player_info']['player_name'], str(player['player_uid']),
                        TickToLocal(player['player_info']['last_online_real_time']),
                        TickToHuman(player['player_info']['last_online_real_time'])))
                except UnicodeEncodeError as e:
                    print("    Player \033[93m %-30s \033[0m\t[\033[92m%s\033[0m] Last Online: %s - %s" % (
                        repr(player['player_info']['player_name']), str(player['player_uid']),
                        TickToLocal(player['player_info']['last_online_real_time']),
                        TickToHuman(player['player_info']['last_online_real_time'])))
            for ind_char in mapObjectMeta['individual_character_handle_ids']:
                guildInstanceMapping[str(ind_char['guid'])] = str(ind_char['instance_id'])
            print()
        # elif str(group_data['value']['GroupType']['value']['value']) == "EPalGroupType::Neutral":
        #     item = group_data['value']['RawData']['value']
        #     print("Neutral Group ID %s  Character Count: %d" % (str(item['group_id']), len(item['individual_character_handle_ids'])))
        #     for ind_char in item['individual_character_handle_ids']:
        #         if ind_char['instance_id'] not in instanceMapping:
        #             print("    \033[31mInvalid Character %s\033[0m" % (str(ind_char['instance_id'])))


def PrettyPrint(data, level=0):
    simpleType = ['DateTime', 'Guid', 'LinearColor', 'Quat', 'Vector', 'PalContainerId']
    if 'struct_type' in data:
        if data['struct_type'] == 'DateTime':
            print("%s<Value Type='DateTime'>%d</Value>" % ("  " * level, data['value']))
        elif data['struct_type'] == 'Guid':
            print("\033[96m%s\033[0m" % (data['value']), end="")
        elif data['struct_type'] == "LinearColor":
            print("%.f %.f %.f %.f" % (data['value']['r'],
                                       data['value']['g'],
                                       data['value']['b'],
                                       data['value']['a']), end="")
        elif data['struct_type'] == "Quat":
            print("%.f %.f %.f %.f" % (data['value']['x'],
                                       data['value']['y'],
                                       data['value']['z'],
                                       data['value']['w']), end="")
        elif data['struct_type'] == "Vector":
            print("%.f %.f %.f" % (data['value']['x'],
                                   data['value']['y'],
                                   data['value']['z']), end="")
        elif data['struct_type'] == "PalContainerId":
            print("\033[96m%s\033[0m" % (data['value']['ID']['value']), end="")
        elif isinstance(data['struct_type'], dict):
            print("%s<%s>" % ("  " * level, data['struct_type']))
            for key in data['value']:
                PrettyPrint(data['value'], level + 1)
            print("%s</%s>" % ("  " * level, data['struct_type']))
        else:
            PrettyPrint(data['value'], level + 1)
    else:
        for key in data:
            if not isinstance(data[key], dict):
                print("%s<%s type='unknow'>%s</%s>" % ("  " * level, key, data[key], key))
                continue
            if 'struct_type' in data[key] and data[key]['struct_type'] in simpleType:
                print("%s<%s type='%s'>" % ("  " * level, key, data[key]['struct_type']), end="")
                PrettyPrint(data[key], level + 1)
                print("</%s>" % (key))
            elif 'type' in data[key] and data[key]['type'] in ["IntProperty", "Int64Property", "BoolProperty"]:
                print("%s<%s Type='%s'>\033[95m%d\033[0m</%s>" % (
                    "  " * level, key, data[key]['type'], data[key]['value'], key))
            elif 'type' in data[key] and data[key]['type'] == "FloatProperty":
                print("%s<%s Type='%s'>\033[95m%f\033[0m</%s>" % (
                    "  " * level, key, data[key]['type'], data[key]['value'], key))
            elif 'type' in data[key] and data[key]['type'] in ["StrProperty", "ArrayProperty", "NameProperty"]:
                print("%s<%s Type='%s'>\033[95m%s\033[0m</%s>" % (
                    "  " * level, key, data[key]['type'], data[key]['value'], key))
            elif isinstance(data[key], list):
                print("%s<%s Type='%s'>%s</%s>" % ("  " * level, key, data[key]['struct_type'] if 'struct_type' in data[
                    key] else "\033[31munknow struct\033[0m", str(data[key]), key))
            else:
                print("%s<%s Type='%s'>" % ("  " * level, key, data[key]['struct_type'] if 'struct_type' in data[
                    key] else "\033[31munknow struct\033[0m"))
                PrettyPrint(data[key], level + 1)
                print("%s</%s>" % ("  " * level, key))


def Save(exit_now=True):
    print("processing GVAS to Sav file...", end="", flush=True)
    if "Pal.PalWorldSaveGame" in gvas_file.header.save_game_class_name or "Pal.PalLocalWorldSaveGame" in gvas_file.header.save_game_class_name:
        save_type = 0x32
    else:
        save_type = 0x31
    sav_file = compress_gvas_to_sav(gvas_file.write(SKP_PALWORLD_CUSTOM_PROPERTIES), save_type)
    print("Done")

    print("Saving Sav file...", end="", flush=True)
    with open(output_path, "wb") as f:
        f.write(sav_file)
    print("Done")
    print("File saved to %s" % output_path)
    if exit_now:
        sys.exit(0)


if __name__ == "__main__":
    main()
