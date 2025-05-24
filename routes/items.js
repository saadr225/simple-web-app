const express = require('express');
const router = express.Router();
const Item = require('../models/Item');

router.get('/', async (req, res) => {
  const items = await Item.find().sort({ date: -1 });
  res.json(items);
});

router.post('/', async (req, res) => {
  const newItem = new Item({ name: req.body.name });
  const savedItem = await newItem.save();
  res.json(savedItem);
});

router.delete('/:id', async (req, res) => {
  try {
    const item = await Item.findById(req.params.id);
    if (!item) return res.status(404).json({ success: false, msg: 'Item not found' });
    
    await Item.findByIdAndDelete(req.params.id);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const item = await Item.findById(req.params.id);
    if (!item) return res.status(404).json({ success: false, msg: 'Item not found' });
    
    const updatedItem = await Item.findByIdAndUpdate(
      req.params.id, 
      { $set: { completed: !item.completed } },
      { new: true }
    );
    res.json(updatedItem);
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;
