PY_FILES := $(wildcard ../src/*.py) $(wildcard ../src/*/*.py) $(wildcard ../src/*/*/*.py)

all:	ru/LC_MESSAGES/game.mo en_US/LC_MESSAGES/game.mo

game.pot: 
	xgettext -L python -o $@ $(PY_FILES)

new_ru.po: game.pot
	msgmerge ru.po game.pot > $@

ru/LC_MESSAGES/game.mo: new_ru.po
	mkdir -p ru/LC_MESSAGES/
	msgfmt -o $@ $<

new_en_US.po: game.pot
	msgmerge en_US.po game.pot > $@

en_US/LC_MESSAGES/game.mo: new_en_US.po
	mkdir -p en_US/LC_MESSAGES/
	msgfmt -o $@ $<

clean:
	rm -f ru.po en_US.po game.pot
	mv new_ru.po ru.po
	mv new_en_US.po en_US.po
